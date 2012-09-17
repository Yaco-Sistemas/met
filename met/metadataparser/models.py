from django.db import models
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

# Create your models here.

class Metadata(models.Model):

    file = models.FileField(upload_to='metadata',
                            verbose_name=_(u'metadata xml file'))
    url = models.URLField(verbose_name='Metadata url',
                          help_text=_(u'Fetch metadata file from this url'))
    owner = models.ForeignKey(User, verbose_name=_('Owner'))
    creation_time = models.DateTimeField(verbose_name=_(u'Creation time'),
                                         auto_now_add=True)
    modification_time = models.DateTimeField(verbose_name=_(u'Modification time'),
                                             auto_now=True)


class Entity(models.Model):

    metadata_file = models.OneToOneField(Metadata, blank=True, null=True,
                                         verbose_name=_(u'Metadata file'))
    entity_group = models.ForeignKey('EntityGroup', blank=True, null=True,
                                     verbose_name=_(u'Entity group'))
    entityid = models.CharField(blank=False, max_length=200,
                                verbose_name=_(u'Entity ID'))
    creation_time = models.DateTimeField(verbose_name=_(u'Creation time'),
                                         auto_now_add=True)
    modification_time = models.DateTimeField(verbose_name=_(u'Modification time'),
                                             auto_now=True)

    class Meta:
        verbose_name = _(u'Entity')
        verbose_name_plural = _(u'Entities')
        ordering = ('-creation_time', )



class EntityGroup(models.Model):

    metadata_file = models.OneToOneField(Metadata, blank=False,
                                      verbose_name=_(u'Metadata file'))

    name = models.CharField(blank=False, max_length=200,
                            verbose_name=_(u'Entity Group Name'))
