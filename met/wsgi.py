import os
import sys

current_directory = os.path.dirname(__file__)
module_name = os.path.basename(current_directory)
sys.path.append(current_directory)

os.environ['DJANGO_SETTINGS_MODULE'] = 'met.settings'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
