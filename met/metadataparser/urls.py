from django.conf.urls import patterns, url


urlpatterns = patterns('met.metadataparser.views',
    url(r'^federation/add/$', 'federation_edit', name='federation_add'),
    url(r'^federation/(?P<federation_slug>[-\w]+)/edit/$', 'federation_edit',
        name='federation_edit'),
    url(r'^federation/(?P<federation_slug>[-\w]+)/delete/$', 'federation_delete',
        name='federation_delete'),
    url(r'^federation/(?P<federation_slug>[-\w]+)/$', 'federation_view',
        name='federation_view'),
    url(r'^federation/(?P<federation_slug>[-\w]+)/entityadd/$', 'entity_edit',
        name='entity_add'),
    url(r'^entity/(?P<entity_id>.+)/edit/$', 'entity_edit', name='entity_edit'),
    url(r'^entity/(?P<entity_id>.+)/delete/$', 'entity_delete', name='entity_delete'),
    url(r'^entity/(?P<entityid>.+)/$', 'entity_view', name='entity_view'),

    url(r'^search_service/$', 'search_service', name='search_service'),
    )
