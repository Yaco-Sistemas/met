from os import path
import requests
from urlparse import urlsplit

from django.db import models
from django.db.models.signals import pre_save
from django.db.models.query import QuerySet
from django.dispatch import receiver
from django.core.files.base import ContentFile

from django.utils.translation import ugettext_lazy as _

from met.metadataparser.xmlparser import MetadataParser


def update_obj(mobj, obj, attrs=None):
    for_attrs = attrs or mobj.all_attrs
    for attrb in attrs or for_attrs:
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
        metadata = MetadataParser(filename=self.file.path)
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
            self._metadata_cache = self.load_file()
        return self._metadata_cache

    def __unicode__(self):
        return self.name

    def get_entity_metadata(self, entityid):
        return self._metadata.get_entity(entityid)

    def get_entity(self, entityid):
        return self.entity_set.get(entityid=entityid)

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
        for entityid in self._metadata.get_entities():
            m_id = entityid
            try:
                entity = self.get_entity(entityid=m_id)
            except Entity.DoesNotExist:
                try:
                    entity = Entity.objects.get(entityid=m_id)
                    self.entity_set.add(entity)
                except Entity.DoesNotExist:
                    entity = self.entity_set.create(entityid=m_id)


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
                    cached_federations[federation.id] = federation
                    entity.load_metadata(federation=federation)

            yield entity


class EntityManager(models.Manager):
    def get_query_set(self):
        return EntityQuerySet(self.model, using=self._db)


class Entity(Base):

    entityid = models.CharField(blank=False, max_length=200, unique=True,
                                verbose_name=_(u'EntityID'), db_index=True)
    federations = models.ManyToManyField(Federation,
                                         verbose_name=_(u'Federations'))

    objects = EntityManager()

    @property
    def organization(self):
        return self._get_property('organization')

    @property
    def name(self):
        return self._get_property('displayName')

    @property
    def types(self):
        return self._get_property('entity_types')

    class Meta:
        verbose_name = _(u'Entity')
        verbose_name_plural = _(u'Entities')

    def __unicode__(self):
        return self.entityid

    def load_metadata(self, federation=None, entity_data=None):
        if not hasattr(self, '_entity_cached'):
            if self.file:
                self._entity_cached = self.load_file().get_entity(self.entityid)
            elif federation:
                self._entity_cached = federation.get_entity_metadata(self.entityid)
            elif entity_data:
                self._entity_cached = entity_data
            else:
                federations = self.federations.all()
                if federations:
                    federation = federations[0]
                else:
                    raise ValueError("Can't find entity metadata")
                self._entity_cached = federation.get_entity_metadata(self.entityid)

    def _get_property(self, prop):
        self.load_metadata()
        if hasattr(self, '_entity_cached'):
            return self._entity_cached.get(prop, None)
        else:
            raise ValueError("Not metadata loaded")

    def process_metadata(self, entity_data=None):
        if not entity_data:
            self.load_metadata()

        if self.entityid != entity_data.get('entityid'):
            raise ValueError("EntityID is not the same")

        self._entity_cached = entity_data


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
def federation_pre_save(sender, instance, **kwargs):
    if instance.file_url:
        instance.fetch_metadata_file()


@receiver(pre_save, sender=Entity, dispatch_uid='entity_pre_save')
def entity_pre_save(sender, instance, **kwargs):
    if instance.file_url:
        instance.fetch_metadata_file()
