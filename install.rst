Metadata Explorer Tool Install
==============================


Install requirements
********************

 * System packages (ubuntu-1204)
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

 * postgresql

    .. code-block::

       sudo su - postgres
       createuser -P met
       createdb --owner met met


Project deployment
******************

 * Create a user met

    .. code-block::

       sudo adduser met

 * Add www-data into met group

    .. code-block::

       sudo adduser www-data met

 * change to met user:

    .. code-block::

       sudo su - met

 * create virtualenv and load it:

    .. code-block::

       virtualenv met-venv
       source met-venv/bin/activate

 * clone git repository:

    .. code-block::

       git clone git://github.com/Yaco-Sistemas/met.git

 * deploy met egg:

    .. code-block::

       cd met
       python setup.py develop

 * Configure local_settings and initialize met database (create models)

    .. code-block::

       cp local_settings.example.py local_settings.py
       python manage.py syncdb


Apache configuration
********************


This is a basic template which use the home of met user

 .. code-block::


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

    WSGIScriptAlias / /home/met/met/wsgi.py

    <Directory /home/met/met/wsgi.py>
    Order allow,deny
    Allow from all
    </Directory>


Initialize media directory
**************************

Initialize media directory with correct permissions

 .. code-block::

    python manage.py collectstatic
    mkdir ~/media
    chmod g+srw ~/media


Saml2 Authentication integration
********************************

(( COMPLETE THIS ))

