.. _api:

Api Description
===============

Metadata Explorer Tool (MET) publish data through a very simple API. The
exported content are properties extracted from Metadata XML files, but the
format of the exported data is not the same than the one of these files.

Only read-only queries are supported.

All queries that MET supports can be exported to XML, JSON and CSV
formats.


General information
*******************

Variables
---------

In the query url format, ${variable} can be one of these:

base_url
   We assume that the home url is known. base_url is the url of
   MET web application home.

format
   Is the output style. Allowed values: xml, json, csv.

federation_slug
   Is the url firendly version of a federation name.


Federations Lists
*****************

Available Queries
-----------------

1. Interfederations summary:

   Description
       Federations of federations.
   url
       ${base_url}/?export=interfederations&format=${format}

2. Federations summary:

   Description
       Federations without interfederations.
   url
       ${base_url}/?export=federations&format=${format}


Output information
------------------

* Federations name
* Number of entities owned by federation
* Number of Service Provider (SP) entities owned by federation
* Number of Identity Provider Service (IDP) entities owned by federation


Federation Item
***************

A federation is not an exportable object. MET exports the entities of a federation
in the federation view.


Entities Lists
**************

Available Queries
-----------------

1. One federation entities:

   Description:
       All entities owned by one federation.
   url
       ${base_url}/met/federation/${federation_slug}/?format=${format}

2. Entities search:

   Description
       An entities searcher by a full or partial entityid.
   url
       ${base_url}/met/search_service/?entityid=${word_to_search}&format=${format}


3. Most federated entities:

   Description
       The three most federated entities
   url
       ${base_url}/?format=${format}&export=most_federated_entities:


Output information
------------------

* EntityID
* Service Types (IDP, SP)
* Federations (List of federations names)


Entity Item
***********

Entities or Services are accessible by a url-quoted entityid.

Available Queries
-----------------

1. Entity object:

   Description
       All information from one entity.
   url
       ${base_url}/met/entity/${entityid}/?format=${format}

Output Information
------------------

* EntityID
* Display name
* Description
* organizations
* entity_types
* federations
* Logos
