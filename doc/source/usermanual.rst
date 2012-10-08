.. _usernamual:

User Manual
===========


Metadata explorer tool is a fast way to find federations, entities and his
relations through entity/federation metadata file information.

 * You can find information about a entity or federation
 * You can find how many and which services belong to a federation
 * You can find to which federations do an entity belong
 * You can find which federations or entities are part of Edugain


Permissions
***********

 * Only django superusers can add new Federations. You can modify users to
   allow add federations through django admin interface.
 * Federation has a field "Editor users" that allow selected users to edit the
   federation and his entities.
 * Entities has a field "Editor users" too, this allow select which users can
   edit only this entity.
 * Anonymous users can watch all datas, but can't edit anything.


Creating federations
********************

When you go to add a new federation, a metadata xml file or a url pointing to
this metadata file is not required. Federation name is required too.

If metadata file has ID attribute on his root, then can put in File ID field.
If you remove his value, then file will be processed when save federation.

If metadata url is set, when federation is save, metadata url file will be
fetched and verified his checksum with present metadata xml file if it exists.

If metadata file is present, it will be parsed and creating on linking entities
if they exists to the created federation.

Creating entities
*****************

You can add new entities from Federation view.

One entity can has his metadata file or url pointing to his metadata file.

EntityID is required
