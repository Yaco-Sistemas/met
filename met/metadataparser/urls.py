from django.conf.urls import patterns, include, url


entity_urlpatterns = patterns('met.metadataparser.views',
    url(r'^$', 'entities_list', name='entities_list'),
    url(r'^(?P<entity_id>\d+)/$', 'entity_view', name='entity_view'),
    url(r'^(?P<entity_id>\d+)/edit/$', 'entity_edit', name='entity_edit'),
    url(r'^add/$', 'entity_edit', name='entity_add'),
    )


urlpatterns = patterns('met.metadataparser.views',
    url(r'^metadata/$', 'metadatas_list', name='metadatas_list'),
    url(r'^metadata/(?P<metadata_id>\d+)/$', 'metadata_view',
        name='metadata_view'),
    url(r'^metadata/(?P<metadata_id>\d+)/edit/$', 'metadata_edit',
        name='metadata_edit'),
    url(r'^metadata/add/$', 'metadata_edit', name='metadata_add'),
    url(r'^federation/$', 'federation_list', name='federation_list'),
    url(r'^federation/(?P<federation_id>\d+)/$', 'federation_view',
        name='federation_view'),
    url(r'^federation/(?P<federation_id>\d+)/edit/$', 'federation_edit',
        name='federation_edit'),
    url(r'^federation/add/$', 'federation_edit', name='federation_add'),
    url(r'^federation/(?P<federation_id\d)/entities/$',
        include(entity_urlpatterns),
    )
