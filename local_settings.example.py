import os
import saml2
BASEDIR = os.path.abspath(os.path.dirname(__file__))


DEBUG = False
TEMPLATE_DEBUG = DEBUG


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'met',                      # Or path to database file if using sqlite3.
        'USER': 'met',                      # Not used with sqlite3.
        'PASSWORD': 'met',                  # Not used with sqlite3.
        'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

INTERNAL_IPS = ('192.168.122.1',)

MEDIA_ROOT = os.path.join(os.environ.get('HOME', '/home/met'), 'media')
STATIC_ROOT = os.path.join(os.environ.get('HOME', '/home/met'), 'static')


SAML_ATTRIBUTE_MAPPING = {
    'mail': ('username', 'email', ),
    'cn': ('first_name', ),
    'sn': ('last_name', ),
}


ORGANIZATION_NAME = 'Your organization'

SAML2DIR = os.path.join(BASEDIR, 'saml2')

SAML_CONFIG = {
  # full path to the xmlsec1 binary programm
  'xmlsec_binary': '/usr/bin/xmlsec1',

  # your entity id, usually your subdomain plus the url to the metadata view
  'entityid': 'http://met.example.com/saml2/metadata/',

  # directory with attribute mapping
  'attribute_map_dir': os.path.join(SAML2DIR, 'attribute-maps'),

  # this block states what services we provide
  'service': {
      # we are just a lonely SP
      'sp': {
          'name': 'Metadata Explorer Tool',
          'endpoints': {
              # url and binding to the assetion consumer service view
              # do not change the binding or service name
              'assertion_consumer_service': [
                  ('http://met.example.com/saml2/acs/',
                   saml2.BINDING_HTTP_POST),
                  ],
              # url and binding to the single logout service view
              # do not change the binding or service name
              'single_logout_service': [
                  ('http://met.example.com/saml2/ls/',
                   saml2.BINDING_HTTP_REDIRECT),
                  ],
              },
          # # This is commented to be compatible with simplesamlphp
          # # attributes that this project need to identify a user
          #'required_attributes': ['mail'],
          #
          # # attributes that may be useful to have but not required
          #'optional_attributes': ['eduPersonAffiliation'],

          # in this section the list of IdPs we talk to are defined
          'idp': {
              # we do not need a WAYF service since there is
              # only an IdP defined here. This IdP should be
              # present in our metadata

              # the keys of this dictionary are entity ids
              'https://idp.example.com/simplesaml/saml2/idp/metadata.php': {
                  'single_sign_on_service': {
                      saml2.BINDING_HTTP_REDIRECT: 'https://idp.example.com/simplesaml/saml2/idp/SSOService.php',
                      },
                  'single_logout_service': {
                      saml2.BINDING_HTTP_REDIRECT: 'https://idp.example.com/simplesaml/saml2/idp/SingleLogoutService.php',
                      },
                  },
              },
          },
      },

 # where the remote metadata is stored
  'metadata': {
      'local': [os.path.join(SAML2DIR, 'remote_metadata.xml')],
      },

  # set to 1 to output debugging information
  'debug': 1,

  # certificate
  'key_file': os.path.join(SAML2DIR, 'certs/server.key'),  # private part
  'cert_file': os.path.join(SAML2DIR, 'certs/server.crt'),  # public part

  # own metadata settings
  'contact_person': [
      {'given_name': 'Sysadmin',
       'sur_name': '',
       'company': 'Example CO',
       'email_address': 'sysadmin@example.com',
       'contact_type': 'technical'},
      {'given_name': 'Admin',
       'sur_name': 'CEO',
       'company': 'Example CO',
       'email_address': 'admin@example.com',
       'contact_type': 'administrative'},
      ],
  # you can set multilanguage information here
  'organization': {
      'name': [('Example CO', 'es'), ('Example CO', 'en')],
      'display_name': [('Example', 'es'), ('Example', 'en')],
      'url': [('http://www.example.com', 'es'), ('http://www.example.com', 'en')],
      },
  }
