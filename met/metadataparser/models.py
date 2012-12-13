from os import path
import requests
from urlparse import urlsplit
from urllib import quote_plus

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.cache import get_cache
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Count
from django.db.models.signals import pre_save
from django.db.models.query import QuerySet
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from met.metadataparser.utils import compare_filecontents
from met.metadataparser.xmlparser import MetadataParser, DESCRIPTOR_TYPES_DISPLAY


TOP_LENGTH = getattr(settings, "TOP_LENGTH", 5)

def update_obj(mobj, obj, attrs=None):
    for_attrs = attrs or getattr(mobj, 'all_attrs', [])
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
                            help_text=_("if url is set, metadata url will be "
                                        "fetched and replace file value"))
    file_id = models.CharField(blank=True, null=True, max_length=100,
                               verbose_name=_(u'File ID'))

    editor_users = models.ManyToManyField(User, null=True, blank=True,
                                          verbose_name=_('editor users'))

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
        if self.file:
            self.file.seek(0)
            original_file_content = self.file.read()
            if compare_filecontents(original_file_content, req.content):
                return

        filename = path.basename(parsed_url.path)
        self.file.save(filename, ContentFile(req.content), save=False)

    def process_metadata(self):
        raise NotImplemented()

    def can_edit(self, user):
        return (user.is_superuser or user in self.editor_users.all())


class XmlDescriptionError(Exception):
    pass


class Federation(Base):

    name = models.CharField(blank=False, null=False, max_length=100,
                            unique=True, verbose_name=_(u'Name'))
    url = models.URLField(verbose_name='Federation url',
                          blank=True, null=True)
    logo = models.ImageField(upload_to='federation_logo', blank=True,
                             null=True, verbose_name=_(u'Federation logo'))
    is_interfederation = models.BooleanField(default=False, db_index=True,
                                         verbose_name=_(u'Is interfederation'))
    slug = models.SlugField(max_length=200, unique=True)

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

    def process_metadata_entities(self, request=None):
        entities_from_xml = self._metadata.get_entities()

        for entity in self.entity_set.all():
            """Remove entity relation if does not exist in metadata"""
            if not self._metadata.entity_exist(entity.entityid):
                self.entity_set.remove(entity)
                if request and not entity.federations.exists():
                    messages.warning(request,
                        mark_safe(_("Orphan entity: <a href='%s'>%s</a>" %
                                (entity.get_absolute_url(), entity.entityid))))

        for m_id in entities_from_xml:
            try:
                entity = self.get_entity(entityid=m_id)
            except Entity.DoesNotExist:
                try:
                    entity = Entity.objects.get(entityid=m_id)
                    self.entity_set.add(entity)
                except Entity.DoesNotExist:
                    entity = self.entity_set.create(entityid=m_id)
            entity.process_metadata(self._metadata.get_entity(m_id))

    def get_absolute_url(self):
        return reverse('federation_view', args=[self.slug])


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

                for federation in federations:
                    if not federation.id in cached_federations:
                        cached_federations[federation.id] = federation

                    cached_federation = cached_federations[federation.id]
                    try:
                        entity.load_metadata(federation=cached_federation)
                    except ValueError:
                        # Allow entity in federation but not in federation file
                        continue
                    else:
                        break

            yield entity


class EntityManager(models.Manager):
    def get_query_set(self):
        return EntityQuerySet(self.model, using=self._db)


class EntityType(models.Model):
    name = models.CharField(blank=False, max_length=20, unique=True,
                            verbose_name=_(u'Name'), db_index=True)
    xmlname = models.CharField(blank=False, max_length=20, unique=True,
                            verbose_name=_(u'Name in XML'), db_index=True)

    def __unicode__(self):
        return self.name


class Entity(Base):

    READABLE_PROTOCOLS = {
        'urn:oasis:names:tc:SAML:1.1:protocol': 'SAML 1.1',
        'urn:oasis:names:tc:SAML:2.0:protocol': 'SAML 2.0',
        'urn:mace:shibboleth:1.0': 'Shiboleth 1.0',
    }

    entityid = models.CharField(blank=False, max_length=200, unique=True,
                                verbose_name=_(u'EntityID'), db_index=True)
    federations = models.ManyToManyField(Federation,
                                         verbose_name=_(u'Federations'))

    types = models.ManyToManyField(EntityType, verbose_name=_(u'Type'))
    objects = models.Manager()
    longlist = EntityManager()

    @property
    def organization(self):
        return self._get_property('organization')

    @property
    def name(self):
        return self._get_property('displayname')

    @property
    def description(self):
        return self._get_property('description')

    @property
    def xml_types(self):
        return self._get_property('entity_types')

    @property
    def protocols(self):
        return self._get_property('protocols')

    def display_protocols(self):
        protocols = []
        for proto in self._get_property('protocols'):
            protocols.append(self.READABLE_PROTOCOLS.get(proto, proto))
        return protocols

    @property
    def logos(self):
        return list(self._get_property('logos')) + list(self.entitylogo_set.all())

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
                for federation in self.federations.all():
                    try:
                        entity_cached = federation.get_entity_metadata(self.entityid)
                        if entity_cached and hasattr(self, '_entity_cached'):
                            self._entity_cached.update(entity_cached)
                        else:
                            self._entity_cached = entity_cached
                    except ValueError:
                        continue
            if not hasattr(self, '_entity_cached'):
                raise ValueError("Can't find entity metadata")

    def _get_property(self, prop):
        try:
            self.load_metadata()
        except ValueError:
            return None
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
        if self.xml_types:
            for etype in self.xml_types:
                try:
                    entity_type = EntityType.objects.get(xmlname=etype)
                except EntityType.DoesNotExist:
                    entity_type = EntityType.objects.create(xmlname=etype,
                                              name=DESCRIPTOR_TYPES_DISPLAY[etype])
                if entity_type not in self.types.all():
                    self.types.add(entity_type)

    def to_dict(self):
        self.description
        entity = self._entity_cached.copy()
        entity["types"] = [(unicode(f)) for f in self.types.all()]
        entity["federations"] = [{u"name": unicode(f), u"url":f.get_absolute_url()}
                                    for f in self.federations.all()]
        if "file_id" in entity.keys():
            del entity["file_id"]
        if "entity_types" in entity.keys():
            del entity["entity_types"]

        return entity

    def can_edit(self, user):
        if super(Entity, self).can_edit(user):
            return True
        for federation in self.federations.all():
            if federation.can_edit(user):
                return True

    @classmethod
    def get_most_federated_entities(self, maxlength=TOP_LENGTH, cache_expire=None):

        entities = None
        if cache_expire:
            cache = get_cache("default")
            entities = cache.get("most_federated_entities")

        if not entities:
            # Entities with count how many federations belongs to, and sorted by most first
            entities = Entity.objects.all().annotate(
                                 federationslength=Count("federations")).order_by("-federationslength")[:maxlength]

        if cache_expire:
            cache = get_cache("default")
            cache.set("most_federated_entities", entities, cache_expire)

        return entities

    def get_absolute_url(self):
        return reverse('entity_view', args=[quote_plus(self.entityid)])


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
    if instance.name:
        instance.slug = slugify(unicode(instance))[:200]


@receiver(pre_save, sender=Entity, dispatch_uid='entity_pre_save')
def entity_pre_save(sender, instance, **kwargs):
    if instance.file_url:
        instance.fetch_metadata_file()
        instance.process_metadata()
