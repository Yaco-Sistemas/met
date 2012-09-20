from datetime import datetime
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


class ParseMetadata(object):

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

    def get_federation(self):
        return ParseFederationMetadata(self.etree)

    def find_entity(self, entityid):
        print "%s[@entityID='%s']" % (
                                    addns('EntityDescriptor'), entityid)
        return ParseEntityMetadata(self.etree.find("%s[@entityID='%s']" % (
                                    addns('EntityDescriptor'), entityid)))

    def get_entity(self):
        return ParseEntityMetadata(self.etree)


class ParseFederationMetadata(object):

    all_attrs = ('valid_until', 'name', 'cache_duration', )

    def __init__(self, etree):
        self.etree = etree
        self.valid_until = self.etree.get('validUntil', None)

        self.name = self.etree.get('Name', None)
        self.cache_duration = self.etree.get('cacheDuration', None)

    def get_entities(self):
        return [ParseEntityMetadata(entity_etree)
                for entity_etree in self.etree.findall(ENTITY_ROOT_TAG)]


class ParseEntityMetadata(object):

    all_attrs = ('entityid', 'valid_until', 'organization', 'contacts',
                 'certificates', 'endpoints', 'display_name',
                 'geolocationhint', 'logos',)

    def __init__(self, etree):
        self.etree = etree

    @property
    def entityid(self):
        if 'entityID' in self.etree.attrib:
            return self.etree.attrib['entityID']

    @property
    def valid_until(self):
        if 'validUntil' in self.etree.attrib:
            value = self.etree.attrib['validUntil']
            try:
                return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
            except ValueError:  # Bad datetime format
                pass

    @property
    def organization(self):
        languages = {}
        for org_node in self.etree.findall(addns('Organization')):
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
    def contacts(self):
        result = []
        for contact_node in self.etree.findall(addns('ContactPerson')):
            contact = {}

            if 'contactType' in contact_node.attrib:
                contact['type'] = contact_node.attrib['contactType']

            for child in contact_node:
                contact[delns(child.tag)] = child.text

            result.append(contact)
        return result

    @property
    def certificates(self):
        result = []

        def collect_certificates_for_role(role):
            key_descr_path = [addns(role), addns('KeyDescriptor')]

            for key_descriptor in self.etree.findall('/'.join(key_descr_path)):
                cert_path = [addns('KeyInfo', XMLDSIG_NAMESPACE),
                             addns('X509Data', XMLDSIG_NAMESPACE),
                             addns('X509Certificate', XMLDSIG_NAMESPACE)]
                for cert in key_descriptor.findall('/'.join(cert_path)):
                    if 'use' in key_descriptor.attrib:
                        result.append({'use': key_descriptor.attrib['use'],
                                   'text': cert.text})
                    else:
                        result.append({'use': 'signing and encryption',
                                       'text': cert.text})

        collect_certificates_for_role('IDPSSODescriptor')
        collect_certificates_for_role('SPSSODescriptor')

        return result

    @property
    def endpoints(self):
        result = []

        def populate_endpoint(node, endpoint):
            for attr in ('Binding', 'Location'):
                if attr in node.attrib:
                    endpoint[attr] = node.attrib[attr]

        for role, endpoints in {
            'IDPSSODescriptor': [
                'Artifact Resolution Service',
                'Assertion ID Request Service',
                'Manage Name ID Service',
                'Name ID Mapping Service',
                'Single Logout Service',
                'Single Sign On Service',
                ],
            'SPSSODescriptor': [
                'Artifact Resolution Service',
                'Assertion Consumer Service',
                'Manage Name ID Service',
                'Single Logout Service',
                'Request Initiator',
                'Discovery Response',
                ],
            }.items():

            for endpoint in endpoints:
                endpoint_id = endpoint.replace(' ', '')  # remove spaces
                path = [addns(role), addns(endpoint_id)]
                for endpoint_node in self.etree.findall('/'.join(path)):
                    endpoint = {'Type': endpoint}
                    populate_endpoint(endpoint_node, endpoint)
                    result.append(endpoint)

        return result

    @property
    def entity_type(self):
        sp = self.etree.findall(addns('SPSSODescriptor'))
        idp = self.etree.findall(addns('IDPSSODescriptor'))
        if len(idp):
            return 'idp'
        elif len(sp):
            return 'sp'
        else:
            raise ValueError("Can't select SP or IDP Entity Type")

    @property
    def display_name(self):
        languages = {}
        path = [addns('SPSSODescriptor'), addns('Extensions'),
                addns('UIInfo', MDUI_NAMESPACE),
                addns('DisplayName', MDUI_NAMESPACE)]
        for dn_node in self.etree.findall('/'.join(path)):
            lang = getlang(dn_node)
            if lang is None:
                continue  # the lang attribute is required

            languages[lang] = dn_node.text

        return languages

    @property
    def geolocationhint(self):
        path = [addns('SPSSODescriptor'), addns('Extensions'),
                addns('UIInfo', MDUI_NAMESPACE),
                addns('GeolocationHint', MDUI_NAMESPACE)]
        result = self.etree.find('/'.join(path))
        if result is not None:
            latitude, longitude = result.text.replace('geo:', '').split(',')
            return {'latitude': latitude, 'longitude': longitude}
        else:
            return None

    @property
    def logos(self):
        languages = {}
        path = [addns('SPSSODescriptor'), addns('Extensions'),
                addns('UIInfo', MDUI_NAMESPACE),
                addns('Logo', MDUI_NAMESPACE)]
        for logo_node in self.etree.findall('/'.join(path)):
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
