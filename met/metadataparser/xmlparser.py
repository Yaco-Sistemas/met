from lxml import etree


NAMESPACES = {
    'xml': 'http://www.w3.org/XML/1998/namespace',
    'xs': 'xs="http://www.w3.org/2001/XMLSchema',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    'md': 'urn:oasis:names:tc:SAML:2.0:metadata',
    'mdui': 'urn:oasis:names:tc:SAML:metadata:ui',
    'ds': 'http://www.w3.org/2000/09/xmldsig#',
    'saml': 'urn:oasis:names:tc:SAML:2.0:assertion',
    'samlp': 'urn:oasis:names:tc:SAML:2.0:protocol',
    }

SAML_METADATA_NAMESPACE = NAMESPACES['md']

XML_NAMESPACE = NAMESPACES['xml']
XMLDSIG_NAMESPACE = NAMESPACES['ds']
MDUI_NAMESPACE = NAMESPACES['mdui']

DESCRIPTOR_TYPES = ('RoleDescriptor', 'IDPSSODescriptor',
                    'SPSSODescriptor', 'AuthnAuthorityDescriptor',
                    'AttributeAuthorityDescriptor', 'PDPDescriptor',
                    'AffiliationDescriptor',)

DESCRIPTOR_TYPES_UTIL = ("md:%s" % item for item in DESCRIPTOR_TYPES)


def addns(node_name, namespace=SAML_METADATA_NAMESPACE):
    '''Return a node name qualified with the XML namespace'''
    return '{' + namespace + '}' + node_name


def delns(node, namespace=SAML_METADATA_NAMESPACE):
    return node.replace('{' + namespace + '}', '')


def getlang(node):
    if 'lang' in node.attrib:
        return node.attrib['lang']
    elif addns('lang', NAMESPACES['xml']) in node.attrib:
        return node.attrib[addns('lang', NAMESPACES['xml'])]

FEDERATION_ROOT_TAG = addns('EntitiesDescriptor')
ENTITY_ROOT_TAG = addns('EntityDescriptor')


class MetadataParser(object):

    def __init__(self, filename=None, data=None):
        if filename:
            try:
                etree_parser = etree.parse(filename)
            except etree.XMLSyntaxError:
                raise ValueError('invalid metadata XML')
        elif data:
            try:
                etree_parser = etree.XML(data)
            except etree.XMLSyntaxError:
                raise ValueError('invalid metadata XML')
        else:
            raise ValueError('filename or data are required')

        self.etree = etree_parser.getroot()
        self.file_id = self.etree.get('ID', None)
        self.is_federation = (self.etree.tag == FEDERATION_ROOT_TAG)
        self.is_entity = not self.is_federation

    def get_federation(self, attrs=None):
        assert self.is_federation
        federation_attrs = attrs or ('ID', 'Name',)
        federation = {}

        for attr in federation_attrs:
            federation[attr] = self.etree.get(attr, None)

        return federation

    def get_entity(self, entityid):
        entity_xpath = self.etree.xpath("md:EntityDescriptor[@entityID='%s']"
                                         % entityid, namespaces=NAMESPACES)
        if len(entity_xpath):
            entity_etree = entity_xpath[0]
        else:
            raise ValueError("Entity not found")
        entity_attrs = (('entityid', 'entityID'), ('file_id', 'ID'))
        entity = {}
        for (dict_attr, etree_attr) in entity_attrs:
            entity[dict_attr] = entity_etree.get(etree_attr, None)

        entity_types = self.entity_types(entity['entityid'])
        if entity_types:
            entity['entity_types'] = entity_types
        displayName = self.entity_displayname(entity['entityid'])
        if displayName:
            entity['displayname'] = displayName
        Organization = self.entity_organization(entity['entityid'])
        if Organization:
            entity['organization'] = Organization

        return entity

    def get_entities(self):
        # Return entityid list
        return self.etree.xpath("//@entityID")

    def entity_organization(self, entityid):
        orgs = self.etree.xpath("//md:EntityDescriptor[@entityID='%s']"
                                "/md:Organization" % entityid,
                                namespaces=NAMESPACES)
        languages = {}
        for org_node in orgs:
            for attr in ('name', 'displayName', 'URL'):
                node_name = 'Organization' + attr[0].upper() + attr[1:]
                for node in org_node.findall(addns(node_name)):
                    lang = getlang(node)
                    if lang is None:
                        continue  # the lang attribute is required

                    lang_dict = languages.setdefault(lang, {})
                    lang_dict[attr] = node.text

        result = []
        for lang, data in languages.items():
            data['lang'] = lang
            result.append(data)
        return result

    def entity_types(self, entityid):
        entity_base = "//md:EntityDescriptor[@entityID='%s']" % entityid

        expression = ("|".join(["%s/%s" % (entity_base, desc)
                                         for desc in DESCRIPTOR_TYPES_UTIL]))
        elements = self.etree.xpath(expression, namespaces=NAMESPACES)
        return [element.tag.split("}")[1] for element in elements]

    def entities_by_type(self, entity_type):
        return self.etree.xpath("//md:EntityDescriptor[//md:%s]/@entityID"
                                % entity_type, namespaces=NAMESPACES)

    def count_entities_by_type(self, entity_type):
        return self.etree.xpath("count(//md:EntityDescriptor[//md:%s])" %s
                               entity_type, namespaces=NAMESPACES)

    def entity_displayname(self, entityid):
        languages = {}
        names = self.etree.xpath("//md:EntityDescriptor[@entityID='%s']"
                                 " //mdui:UIInfo"
                                 "/mdui:DisplayName" % entityid,
                                 namespaces=NAMESPACES)

        for dn_node in names:
            lang = getlang(dn_node)
            if lang is None:
                continue  # the lang attribute is required

            languages[lang] = dn_node.text

        return languages

    def entity_logos(self, entityid):
        languages = {}
        logos = self.etree.xpath("//md:EntityDescriptor[@entityID='%s']"
                                 " //mdui:UIInfo"
                                 "/mdui:Logo" % entityid,
                                 namespaces=NAMESPACES)

        for logo_node in logos:
            lang = getlang(logo_node)
            if lang is None:
                continue  # the lang attribute is required

            lang_dict = languages.setdefault(lang, {})
            lang_dict['width'] = logo_node.attrib.get('width', '')
            lang_dict['height'] = logo_node.attrib.get('height', '')
            lang_dict['location'] = logo_node.text

        result = []
        for lang, data in languages.items():
            data['lang'] = lang
            result.append(data)

        return result
