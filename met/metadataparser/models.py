from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from met.metadataparser.xmlparser import ParseMetadata


def update_obj(mobj, obj):
    for attrb in mobj.all_attrs:
        if (getattr(mobj, attrb, None) and
            getattr(obj, attrb, None) and
            getattr(mobj, attrb) != getattr(obj, attrb)):
            setattr(obj, attrb,  getattr(mobj, attrb))


class Base(models.Model):
    file = models.FileField(upload_to='metadata',
                            verbose_name=_(u'metadata xml file'))
    file_url = models.URLField(verbose_name='Metadata url',
                               blank=True, null=True,
                               help_text=_(u'Url to fetch metadata file'))
    file_id = models.CharField(blank=True, null=True, max_length=100,
                               verbose_name=_(u'File ID'))
    logo = models.ImageField(upload_to='federation_logo', blank=True,
                             null=True, verbose_name=_(u'Federation logo'))

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
        metadata_raw = self.file.read()
        metadata = ParseMetadata(data=metadata_raw)
        #if (hasattr(metadata, 'file_id') and
        #    getattr(metadata, 'file_id') != self.file_id):
        return metadata

    def process_metadata(self):
        raise NotImplemented


class XmlDescriptionError(Exception):
    pass


class Federation(Base):

    name = models.CharField(blank=True, null=True, max_length=100,
                            verbose_name=_(u'Name'))

    def __unicode__(self):
        return self.name

    def get_entity_metadata(self, entityid):
        metadata = self.load_file()
        return metadata.find_entity(entityid)

    def process_metadata(self):
        metadata = self.load_file()
        if not metadata:
            return
        if not metadata.is_federation:
            raise XmlDescriptionError("XML Haven't federation form")

        metadata_federation = metadata.get_federation()
        self._metadata = metadata
        update_obj(metadata_federation, self)

    def process_metadata_entities(self):
        if not self._metadata:
            metadata = self.load_file()
            self._metadata = metadata

        metadata_federation = self._metadata.get_federation()
        entities_metadata = metadata_federation.get_entities()
        for metadata_entity in entities_metadata:
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


class Entity(Base):

    ENTITY_TYPE = (
            ('idp', _('Identity provider')),
            ('sp', _('Service provider')),
        )

    entityid = models.URLField(blank=False, max_length=200, unique=True,
                               verbose_name=_(u'EntityID'), db_index=True)
    entity_type = models.CharField(choices=ENTITY_TYPE, blank=False,
                                   db_index=True, max_length=3,
                                   verbose_name=_(u'Entity Type'))
    federations = models.ManyToManyField(Federation,
                                         verbose_name=_(u'Federation'))

    @property
    def Organization(self):
        return self._get_property('Organization')

    @property
    def name(self):
        return self._get_property('displayName')

    class Meta:
        verbose_name = _(u'Entity')
        verbose_name_plural = _(u'Entities')

    def __unicode__(self):
        return self.name or self.entityid

    def load_metadata(self, federation=None):
        if not hasattr(self, '_metadata'):
            if self.file:
                self._metadata = self.load_file()
            else:
                if not federation:
                    federations = self.federations.all()
                    if federations:
                        federation = federations[0]

                    self._metadata = federation.get_entity_metadata(
                                                           self.entityid)
                else:
                    self._metadata = None
                    raise ValueError("Can't find entity metadata")

    def _get_property(self, prop):
        self.load_metadata()
        return getattr(self._metadata, prop, None)

    def process_metadata(self, metadata=None):
        if not metadata:
            self.load_metadata()
            metadata = self._metadata.get_entity()

        if self.entityid != metadata.entityid:
            raise ValueError("EntityID is not the same")

        update_obj(metadata, self)


@receiver(pre_save, sender=Federation, dispatch_uid='federation_pre_save')
def process_metadata(sender, instance, **kwargs):
    instance.process_metadata()


@receiver(post_save, sender=Federation, dispatch_uid='federation_post_save')
def process_metadata_entities(sender, instance, **kwargs):
    instance.process_metadata_entities()
