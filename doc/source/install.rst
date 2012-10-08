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
* memcached
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

* Create a user met

  .. code-block:: bash

      sudo adduser met

* Add www-data into met group

  .. code-block:: bash

      sudo adduser www-data met

* change to met user:

  .. code-block:: bash

      sudo su - met

* create virtualenv and load it:

  .. code-block:: bash

      virtualenv met-venv
      source met-venv/bin/activate

* clone git repository:

  .. code-block:: bash

      git clone git://github.com/Yaco-Sistemas/met.git

* deploy met egg:

  .. code-block:: bash

      cd met
      python setup.py develop

* Configure local_settings and initialize met database (create models)

  .. code-block:: bash

      cp local_settings.example.py local_settings.py
      python manage.py syncdb


Apache configuration
********************


This is a basic template which use the home of met user

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

    WSGIScriptAlias / /home/met/met/django-wsgi.py

    <Directory /home/met/met/django-wsgi.py>
    Order allow,deny
    Allow from all
    </Directory>


Initialize media directory
**************************

Initialize media directory with correct permissions

.. code-block:: bash

    python manage.py collectstatic
    mkdir ~/media
    chmod g+srw ~/media


Saml2 Authentication integration
********************************

The example local_settings has a generic configuration to integrate with SAML2
Authentication.

You need to change SAML_CONFIG according to your organization information.

For testing purposes, you should create your own self-signed certificates. For
other purposes buy them:

* Follow the first five steps of this guide:
  http://www.akadia.com/services/ssh_test_certificate.html
* Create certs directory met/saml2/certs
* Copy server.key and server.crt to met/saml2/certs

.. code-block:: bash

   openssl genrsa -des3 -out server.key 1024
   openssl req -new -key server.key -out server.csr
   cp server.key server.key.org
   openssl rsa -in server.key.org -out server.key
   openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt


You need to get your IDP metadata and put in saml/remote_metadata.xml or
another path you set in SAML_CONFIG.metatadata.local setting
