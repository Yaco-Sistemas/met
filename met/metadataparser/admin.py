from django.contrib import admin

from met.metadataparser.models import Metadata, Entity, EntityGroup


class MetadataAdmin(admin.ModelAdmin):

    list_display = ('owner', 'creation_time', 'modification_time')


class EntityAdmin(admin.ModelAdmin):
    pass


class EntityGroupAdmin(admin.ModelAdmin):
    pass


admin.site.register(Metadata, MetadataAdmin)
admin.site.register(Entity, EntityAdmin)
admin.site.register(EntityGroup, EntityGroupAdmin)
