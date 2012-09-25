from os import path
import requests
from urlparse import urlsplit

from django.db import models
from django.db.models.signals import pre_save, post_save
from django.db.models.query import QuerySet
from django.dispatch import receiver
from django.core.files.base import ContentFile

from django.utils.translation import ugettext_lazy as _

from met.metadataparser.xmlparser import ParseMetadata


def update_obj(mobj, obj, attrs=None):
    for attrb in attrs or mobj.all_attrs:
        if (getattr(mobj, attrb, None) and
            getattr(obj, attrb, None) and
            getattr(mobj, attrb) != getattr(obj, attrb)):
            setattr(obj, attrb,  getattr(mobj, attrb))


class Base(models.Model):
    file_url = models.URLField(verbose_name='Metadata url',
                               blank=True, null=True,
                               help_text=_(u'Url to fetch metadata file'))
    file = models.FileField(upload_to='metadata', blank=True, null=True,
                            verbose_name=_(u'metadata xml file'),
                            help_text=_("if url is set metadata url will be"
                                        "fetched and replace file value"))

    file_id = models.CharField(blank=True, null=True, max_length=100,
                               verbose_name=_(u'File ID'))

    class Meta:
        abstract = True

    class XmlError(Exception):
        pass

    def __unicode__(self):
        return self.url or u"Metadata %s" % self.id

    def load_file(self):
        """Only load file and parse it, don't create/update any objects"""
        if not self.file:
            return None
        self.file.seek(0)
        metadata_raw = self.file.read()
        metadata = ParseMetadata(data=metadata_raw)
        return metadata

    def fetch_metadata_file(self):
        req = requests.get(self.file_url)
        if req.ok:
            req.raise_for_status()
        parsed_url = urlsplit(self.file_url)
        filename = path.basename(parsed_url.path)
        self.file.save(filename, ContentFile(req.content), save=False)

    def process_metadata(self):
        raise NotImplemented()


class XmlDescriptionError(Exception):
    pass


class Federation(Base):

    name = models.CharField(blank=True, null=True, max_length=100,
                            verbose_name=_(u'Name'))
    url = models.URLField(verbose_name='Federation url',
                          blank=True, null=True)
    logo = models.ImageField(upload_to='federation_logo', blank=True,
                             null=True, verbose_name=_(u'Federation logo'))
    part_of_edugain = models.BooleanField(verbose_name=_(u'Part of eduGAIN'))

    @property
    def _metadata(self):
        if not hasattr(self, '_metadata_cache'):
            self._metadata_cache = self.load_file().get_federation()
        return self._metadata_cache

    def __unicode__(self):
        return self.name

    def get_entity_metadata(self, entityid):
        return self._metadata.find_entity(entityid)

    def process_metadata(self):
        metadata = self.load_file()
        if (self.file_id and metadata.file_id and
                metadata.file_id == self.file_id):
            return
        else:
            self.file_id = metadata.file_id

        if not metadata:
            return
        if not metadata.is_federation:
            raise XmlDescriptionError("XML Haven't federation form")

        update_obj(metadata.get_federation(), self)

    def process_metadata_entities(self):
        self._metadata.get_entities()
        for metadata_entity in self._metadata.get_entities():
            m_id = metadata_entity.entityid
            m_type = metadata_entity.entity_type
            try:
                entity = self.entity_set.get(entityid=m_id)
            except Entity.DoesNotExist:
                try:
                    entity = Entity.objects.get(entityid=m_id)
                    entity.federations.add(self)
                except Entity.DoesNotExist:
                    entity = self.entity_set.create(entityid=m_id,
                                                    entity_type=m_type)
                    entity.process_metadata(metadata_entity)
                    entity.save()


class EntityQuerySet(QuerySet):

    def iterator(self):
        cached_federations = {}
        for entity in super(EntityQuerySet, self).iterator():
            if not entity.file:
                federations = entity.federations.all()
                if federations:
                    federation = federations[0]
                else:
                    raise ValueError("Can't find entity metadata")

                if federation.id in cached_federations:
                    entity.load_metadata(
                             federation=cached_federations[federation.id])
                else:
                    entity.load_metadata(federation=federation)
                    cached_federations[federation.id] = federation

            yield entity


class EntityManager(models.Manager):
    def get_query_set(self):
        return EntityQuerySet(self.model, using=self._db)


class Entity(Base):

    ENTITY_TYPE = (
            ('idp', _('Identity provider')),
            ('sp', _('Service provider')),
        )

    entityid = models.CharField(blank=False, max_length=200, unique=True,
                                verbose_name=_(u'EntityID'), db_index=True)
    entity_type = models.CharField(choices=ENTITY_TYPE, blank=False,
                                   null=False, db_index=True, max_length=3,
                                   default='sp',
                                   verbose_name=_(u'Entity Type'),)
    federations = models.ManyToManyField(Federation,
                                         verbose_name=_(u'Federations'))

    objects = EntityManager()

    @property
    def organization(self):
        return self._get_property('organization')

    @property
    def name(self):
        return self._get_property('displayName')

    class Meta:
        verbose_name = _(u'Entity')
        verbose_name_plural = _(u'Entities')

    def __unicode__(self):
        return self.name or self.entityid

    @property
    def _metadata(self):
        if not hasattr(self, '_metadata_cache'):
            self.load_metadata()
        return self._metadata_cache

    def load_metadata(self, federation=None):
        if not hasattr(self, '_metadata_cache'):
            if self.file:
                self._metadata_cache = self.load_file()
            else:
                if not federation:
                    federations = self.federations.all()
                    if federations:
                        federation = federations[0]
                    else:
                        raise ValueError("Can't find entity metadata")
                self._metadata_cache = federation.get_entity_metadata(
                                                                self.entityid)

    def _get_property(self, prop):
        self.load_metadata()
        return getattr(self._metadata, prop, None)

    def process_metadata(self, metadata=None):
        if not metadata:
            self.load_metadata()
            metadata = self._metadata.get_entity()

        if self.entityid != metadata.entityid:
            raise ValueError("EntityID is not the same")

        update_obj(metadata, self, ('entityid', 'entity_type',))


class EntityLogo(models.Model):
    logo = models.ImageField(upload_to='entity_logo', blank=True,
                             null=True, verbose_name=_(u'Entity logo'))
    alt = models.CharField(max_length=100, blank=True, null=True,
                           verbose_name=(u'Alternative text'))

    entity = models.ForeignKey(Entity, blank=False,
                        verbose_name=_('Entity'))

    def __unicode__(self):
        return self.alt or u"logo %i" % self.id


@receiver(pre_save, sender=Federation, dispatch_uid='federation_pre_save')
def process_metadata(sender, instance, **kwargs):
    if instance.file_url:
        instance.fetch_metadata_file()
    instance.process_metadata()


@receiver(post_save, sender=Federation, dispatch_uid='federation_post_save')
def process_metadata_entities(sender, instance, **kwargs):
    instance.process_metadata_entities()
