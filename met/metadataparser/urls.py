from django.conf.urls import patterns, include, url


urlpatterns = patterns('met.metadataparser.views',
    url(r'^metadata/$', 'metadatas_list', name='metadatas_list'),
    url(r'^metadata/(?P<metadata_id>\d+)/$', 'metadata_view', name='metadata_view'),
    url(r'^metadata/(?P<metadata_id>\d+)/edit/$', 'metadata_edit', name='metadata_edit'),
    url(r'^metadata/add/$', 'metadata_edit', name='metadata_add'),
    )
