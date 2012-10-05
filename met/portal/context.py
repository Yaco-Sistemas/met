from django.conf import settings


def portal_settings(request):
    """ Include some settings value in context """

    copy_attrs = ('LOGIN_URL',
                  'LOGOUT_URL',
		  'ORGANIZATION_NAME')

    custom_settings = {}

    for key in copy_attrs:
        custom_settings[key] = getattr(settings, key, '')

    return {'portal_settings': custom_settings}
