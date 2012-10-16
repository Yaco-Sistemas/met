from django.conf.urls import patterns, include, url
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'met.metadataparser.views.index', name='index'),
    url(r'^met/', include('met.metadataparser.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^saml2/', include('djangosaml2.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^error403.html$', 'met.portal.views.error403'),
    url(r'^error404.html$', 'met.portal.views.error404'),
    url(r'^error500.html$', 'met.portal.views.error500'),


)

handler403 = 'met.portal.views.error403'
handler404 = 'met.portal.views.error404'
handler500 = 'met.portal.views.error500'

if settings.DEBUG:
    from django.views.static import serve
    _media_url = settings.MEDIA_URL
    if _media_url.startswith('/'):
        _media_url = _media_url[1:]
        urlpatterns += patterns('',
                                (r'^%s(?P<path>.*)$' % _media_url,
                                serve,
                                {'document_root': settings.MEDIA_ROOT}))
    del(_media_url, serve)
