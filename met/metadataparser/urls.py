from django.conf.urls import patterns, url


urlpatterns = patterns('met.metadataparser.views',
    url(r'^federation/$', 'federations_list', name='federations_list'),
    url(r'^federation/add/$', 'federation_edit', name='federation_add'),
    url(r'^federation/(?P<federation_id>\d+)/edit/$', 'federation_edit',
        name='federation_edit'),
    url(r'^federation/(?P<federation_id>\d+)/delete/$', 'federation_delete',
        name='federation_delete'),
    url(r'^federation/(?P<federation_id>\d+)/$', 'federation_view',
        name='federation_view'),
    url(r'^federation/(?P<federation_id>\d+)/entityadd/$', 'entity_edit',
        name='entity_add'),
    url(r'^entity/(?P<entity_id>\d+)/$', 'entity_view', name='entity_view'),
    url(r'^entity/(?P<entity_id>\d+)/edit/$', 'entity_edit',
        name='entity_edit'),
    url(r'^entity/(?P<entity_id>\d+)/delete/$', 'entity_delete',
        name='entity_delete'),

    url(r'^search_service/$', 'search_service', name='search_service')
    )
