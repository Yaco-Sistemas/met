.. _api:

Api Description
===============

Metadata Explorer Tool (MET) publish data through a very simple API. The
exported content are properties extracted from Metadata XML files but the
format is not the same.

Only read queries are supported.


All queries MET that support export, can be exported to XML, JSON and CSV
format.


General information
*******************

Variables
---------

In the query url format, ${variable} is a string according to this:

base_url
   We assume that the url index is known. base_url is the url of
   index from MET web application.

format
   is the output style. Allowed values: xml, json, csv.

federation_slug
   is the name of one federation in the url.


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
       Federations list without interfederations.
   url
       ${base_url}/?export=federations&format=${format}


Output information provide
--------------------------

* Federation Name
* Count of entities owned
* Count of Service Provider (SP) entities owned by federation
* Count of Identity Provider Service (IDP) entities owned by federation


Federation Item
***************

There isn't federation object exportable as is. MET export entities federation
in the view of one federation.


Entities Lists
**************

Available Queries
-----------------

1. Entities from one federation:

   Description:
       All entities owned by one federation.
   url
       ${base_url}/met/federation/${federation_slug}/?format=${format}

2. Entities search:

   Description
       A entities searcher by entityid.
   url
       ${base_url}/met/search_service/?entityid=${word_to_search}&format=${format}


3. Most federated entities:

   Description
       Three most federated entities
   url
       ${base_url}/?format=${format}&export=most_federated_entities:


Output information provide
--------------------------

* EntityID
* Service Types (IDP, SP)
* Federations (List of federations names)


Entity Item
***********

Entities or Services are accessible by url quoted entityid.

Available Queries
-----------------

1. Entity object:

   Description
       All information from one entity view.
   url
       ${base_url}/met/entity/${entityid}/?format=${format}

Output Information provide
--------------------------

* EntityID
* Display name
* Description
* organizations
* entity_types
* federations
* Logos
