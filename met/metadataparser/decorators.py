import urlparse
from django.http import HttpResponseForbidden
try:
    from functools import wraps
except ImportError:
    from django.utils.functional import wraps # Python 2.4 fallback

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.utils.decorators import available_attrs



def user_can_edit(objtype, login_url=None,
                  redirect_field=REDIRECT_FIELD_NAME):
    """ based on user_passtest from django.contrib.auth.decorators"""
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            objid = None
            for key in kwargs.keys():
                if key.endswith('_id'):
                    objid = kwargs.get(key)
                    break
            if objtype and objid:
                obj = objtype.objects.get(id=objid)
                if obj.can_edit(request.user):
                    return view_func(request, *args, **kwargs)
                else:
                    permission = False
            elif request.user.is_authenticated():
                return view_func(request, *args, **kwargs)

            if request.user.is_authenticated():
                return HttpResponseForbidden(u"You can't edit this object")


            path = request.build_absolute_uri()
            # If the login url is the same scheme and net location then just
            # use the path as the "next" url.
            login_scheme, login_netloc = urlparse.urlparse(login_url or
                                                        settings.LOGIN_URL)[:2]
            current_scheme, current_netloc = urlparse.urlparse(path)[:2]
            if ((not login_scheme or login_scheme == current_scheme) and
                (not login_netloc or login_netloc == current_netloc)):
                path = request.get_full_path()
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(path, login_url)
        return _wrapped_view
    return decorator
