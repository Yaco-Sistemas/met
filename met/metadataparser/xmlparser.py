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
            with open(filename, 'r') as file:
                data = file.read()
                if not data:
                    raise ValueError('no metadata content')
        elif not data:
            raise ValueError('not data or filename found')

        try:
            self.etree = etree.XML(data)
        except etree.XMLSyntaxError:
            raise ValueError('invalid metadata XML')

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
            entity = entity_xpath[0]
        else:
            raise ValueError("Entity not found")
        entity_attrs = ('entityID', 'Name', 'ID')
        entity = {}
        for attr in entity_attrs:
            entity[attr] = entity.get(attr, None)

        displayName = self.entity_display_name(entity['entityID'])
        if displayName:
            entity['displayName'] = displayName
        Organization = self.entity_organization(entity['entityID'])
        if Organization:
            entity['Organization'] = Organization

    def get_entities(self):
        # Return entityid list
        return self.etree.xpath("//@entityID")

    @property
    def entity_organization(self, entityid):
        orgs = self.etree.xpath("//md:EntityDescriptor[@entityID='%s']"
                                "/md:Organization/" % entityid,
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

    @property
    def entity_type(self, entityid):
        is_sp = self.etree.xpath("count(//md:EntityDescriptor[@entityID='%s']"
                                 "/md:SPSSODescriptor) = 1" % entityid,
                                 namespaces=NAMESPACES)
        if is_sp:
            return 'sp'
        is_idp = self.etree.xpath("count(//md:EntityDescriptor[@entityID='%s']"
                                  "/md:IDPSSODescriptor) = 1" % entityid,
                                  namespaces=NAMESPACES)
        if is_idp:
            return 'idp'

        raise ValueError("Can't select SP or IDP Entity Type")

    @property
    def entity_display_name(self, entityid):
        languages = {}
        names = self.etree.xpath("//md:EntityDescriptor[@entityID='%s']"
                                 "/mdui:UIInfo"
                                 "/mdui:DisplayName" % entityid,
                                 namespaces=NAMESPACES)

        for dn_node in names:
            lang = getlang(dn_node)
            if lang is None:
                continue  # the lang attribute is required

            languages[lang] = dn_node.text

        return languages

    @property
    def entity_logos(self, entityid):
        languages = {}
        logos = self.etree.xpath("//md:EntityDescriptor[@entityID='%s']"
                                 "/mdui:UIInfo"
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
