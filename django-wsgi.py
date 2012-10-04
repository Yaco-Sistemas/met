import os
import sys

current_directory = os.path.dirname(__file__)
module_name = os.path.basename(current_directory)
home_directory = os.environ.get('HOME')
home_directory = '/home/met'

activate_this = os.path.join(home_directory, 'met-venv/bin/activate_this.py')
execfile(activate_this, dict(__file__=activate_this))

sys.path.append(current_directory)
os.environ['DJANGO_SETTINGS_MODULE'] = 'met.settings'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
