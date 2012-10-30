.. _usernamual:

User Manual
===========


The **Metadata Explorer Tool** is a fast way to find federations, entities and
their relationships, through entity/federation metadata information files.

* You can find information about an entity or a federation
* You can find how many and which services belong to a federation
* You can find to which federations do an entity belong
* You can find which federations or entities are part of Edugain


Permissions
***********

* Only django superusers can add new Federations. You can modify the users to
  allow them to add Federations through the django admin interface.
* Federations have a field ``Editor users`` that allow selected users to edit
  the federation and its entities.
* Entities have a field ``Editor users`` too, here we can select which users
  can edit the entity.
* Anonymous users can read all data, but they can't edit anything.


Creating federations
********************

When you are going to add a new federation, its name is required, but a
metadata xml file, or a url pointing to such file, is not.

If the metadata file has an ``ID`` attribute on his root, then it will be
stored in the *File ID* field. If you remove its value, then the metadata file
will be processed again when you save the federation.

If *metadata url* is set, when the federation is saved, the file pointed by
this url will be fetched and its checksum verified against present metadata xml
file if any. If there was a previously stored file, and the checksum doesn't
match, the new file will be processed.

The processing of metadata files consists on creating entities and link them
to their corresponding federations.

A federation can be a interfederation, a group of federations. A
interfederation has same views, edit and permissions that federations. It's
only take effect in index view.

Creating entities
*****************

You can add new entities from Federation view.

As well as federations, entities can have their own metadata file, or a url
pointing to such file.

*EntityID* is a required field.
