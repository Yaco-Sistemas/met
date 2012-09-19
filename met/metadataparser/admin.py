from django.contrib import admin

from met.metadataparser.models import Metadata, Federation, Entity


class MetadataAdmin(admin.ModelAdmin):
    pass


class FederationAdmin(admin.ModelAdmin):
    pass


class EntityAdmin(admin.ModelAdmin):
    pass


admin.site.register(Federation, FederationAdmin)
admin.site.register(Metadata, MetadataAdmin)
admin.site.register(Entity, EntityAdmin)
