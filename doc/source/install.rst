.. _index:

Metadata Explorer Tool Install
==============================


Install requirements
********************

System packages (ubuntu-1204)

* python-setuptools
* python-dev
* python-virtualenv
* python-imaging
* libjpeg-dev
* libpng-dev
* postgresql
* libapache2-mod-wsgi
* build-essential
* libxml2-dev
* libxslt-dev
* libpq-dev
* xmlsec1


Create database
***************

postgresql :

.. code-block:: bash

  sudo su - postgres
  createuser -P met
  createdb --owner met met


Project deployment
******************

* Create a user ``met`` in the system:

  .. code-block:: bash

      sudo adduser met

* Add ``www-data`` into ``met`` group:

  .. code-block:: bash

      sudo adduser www-data met

* Change to ``met`` user:

  .. code-block:: bash

      sudo su - met

* Create a virtualenv and load it:

  .. code-block:: bash

      virtualenv met-venv
      source met-venv/bin/activate

* Clone git repository:

  .. code-block:: bash

      git clone git://github.com/Yaco-Sistemas/met.git

* Deploy met egg:

  .. code-block:: bash

      cd met
      python setup.py develop

* Configure ``local_settings`` and initialize met database (create models):

  .. code-block:: bash

      cp local_settings.example.py local_settings.py
      python manage.py syncdb


Apache configuration
********************

This is a basic template that assumes the project was deployed into ``met``
user's home.

A apache 2.2.18 or later is required (AllowEncodedSlashes NoDecode)
http://httpd.apache.org/docs/2.2/mod/core.html#allowencodedslashes

.. code-block:: text

    Alias /media/ /home/met/media/
    Alias /static/ /home/met/static/

    <Directory /home/met/media/>
    Order deny,allow
    Allow from all
    </Directory>

    <Directory /home/met/static/>
    Order deny,allow
    Allow from all
    </Directory>

    AllowEncodedSlashes NoDecode

    WSGIScriptAlias / /home/met/met/met-wsgi.py

    <Directory /home/met/met/met-wsgi.py>
    Order allow,deny
    Allow from all
    </Directory>


Initialize media directory
**************************

Initialize media directory with proper permissions:

.. code-block:: bash

    python manage.py collectstatic
    mkdir ~/media
    chmod g+srw ~/media


Saml2 Authentication integration
********************************

The ``local_settings`` example has a generic configuration of SAML2
Authentication integration.

You need to change ``SAML_CONFIG`` according to your organization information.

For testing purposes, you should create your own self-signed certificates. For
other purposes you should buy them. How to create the certificates:

* Follow the first five steps of this guide:
  http://www.akadia.com/services/ssh_test_certificate.html
* Create certs directory met/saml2/certs
* Copy server.key and server.crt to met/saml2/certs

.. code-block:: bash

   openssl genrsa -des3 -out server.key 2048
   openssl req -new -key server.key -out server.csr
   cp server.key server.key.org
   openssl rsa -in server.key.org -out server.key
   openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt


You need to put your IDP metadata in ``saml/remote_metadata.xml`` or, if you
modified the ``SAML_CONFIG.metatadata.local`` setting, in the proper path.

Set a saml2 user as superuser
-----------------------------

If the user doesn't exists, you can create it already as superuser without a
password using this command in the correct environment:


.. code-block:: bash

  python manage.py createsuperuser --username super@example.com \
     --email=supera@example.com --noinput

If this fails and some errors appear related to the  djangosaml2.log file, then
you must change the permissions of the /tmp/djangosaml2.log file and make it
writable by the user that executes your manage.py command.


Customizations
==============

Customize /about page
*********************

We are going to create a new `about.html` template that overwrite the default
`about.html` template. To do this, you must ensure that this block exists in your
`local_settings.py` (it is already set in `local_settings.example.py` provided by
this package)

.. code-block:: python

  TEMPLATE_DIRS = (
      # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
      # Always use forward slashes, even on Windows.
      # Don't forget to use absolute paths, not relative paths.
      os.path.join(BASEDIR, 'templates'),
  )

`BASEDIR` is the directory where `local_settings.py` and `met-wsgi.py` are. Then
we need to create a directory called templates and a file called `about.html`
in it. The `about.html` file must have this structure:

::

  {% extends "base.html" %}

  {% block content %}
  <p>This is your custom content</p>
  {% endblock %}

You can add your custom html between the `block` and `endblock` tags.
