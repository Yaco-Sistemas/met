from django.db import models
from django.utils.translation import ugettext_lazy as _


class Metadata(models.Model):
    file = models.FileField(upload_to='metadata',
                            verbose_name=_(u'metadata xml file'))
    url = models.URLField(verbose_name='Metadata url',
                          help_text=_(u'Fetch metadata file from this url'))

    def is_federation(self):
        return (len(self.federation_set.all()) > 0)

    def is_entity(self):
        return (len(self.entity_set.all()) > 0)

    def get_federation_or_entity(self):
        federations = self.federation_set.all()
        entities = self.entity_set.all()
        if len(federations):
            return federations[0]
        elif len(entities):
            return entities[0]
        else:
            return None

    def __unicode__(self):
        return self.url or u"Metadata %s" % self.id


class Federation(models.Model):
    organization = models.CharField(blank=True, null=True, max_length=200,
                                    verbose_name=_(u'Organization'))
    organization_link = models.URLField(blank=True, null=True,
                                        verbose_name='Organization url')
    metadata_file = models.OneToOneField(Metadata, blank=True, null=True,
                                         verbose_name=_(u'Metadata file'))
    logo = models.ImageField(upload_to='federation_logo', blank=True,
                             null=True, verbose_name=_(u'Federation logo'))
    metadata_file = models.ForeignKey(Metadata, blank=True, null=True,
                                      verbose_name=_(u'Metadata file'))

    def __unicode__(self):
        return self.organization


class Entity(models.Model):

    ENTITY_TYPE = (
            ('idp', _('Identity provider')),
            ('sp', _('Service provider')),
        )

    name = models.CharField(blank=False, max_length=200,
                            verbose_name=_(u'Name'))

    entityid = models.URLField(blank=False, max_length=200,
                               verbose_name=_(u'EntityID'))
    entity_type = models.CharField(choices=ENTITY_TYPE, blank=False,
                                  max_length=3, verbose_name=_(u'Entity Type'))
    metadata_file = models.ForeignKey(Metadata, blank=True, null=True,
                                      verbose_name=_(u'Metadata file'))
    federation = models.ForeignKey(Federation, blank=True, null=True,
                                   verbose_name=_(u'Federation'))

    def __unicode__(self):
        return self.name or self.entityid

    class Meta:
        verbose_name = _(u'Entity')
        verbose_name_plural = _(u'Entities')
