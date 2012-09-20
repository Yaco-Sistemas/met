from django.contrib import admin

from met.metadataparser.models import Federation, Entity


class FederationAdmin(admin.ModelAdmin):
    pass


class EntityAdmin(admin.ModelAdmin):
    pass


admin.site.register(Federation, FederationAdmin)
admin.site.register(Entity, EntityAdmin)
