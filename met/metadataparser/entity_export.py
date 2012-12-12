import csv
from xml.dom.minidom import Document

from django.http import HttpResponse, HttpResponseBadRequest
from django.template.defaultfilters import slugify
from django.utils import simplejson as json


def export_entity_csv(entity):
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = ('attachment; filename=%s.csv'
                                       % slugify(entity))
    writer = csv.writer(response)
    edict = entity.to_dict()

    writer.writerow(edict.keys())
    # Write data to CSV file
    row = []
    for (key, value) in edict.items():
        if type(value) is list:
            if len(value) > 0 and type(value[0]) == dict:
                row.append(", ".join([v.values()[0] for v in value]))
            else:
                row.append(", ".join(value))
        elif type(value) in (str, int):
            row.append(value)
        elif type(value) is unicode:
            row.append(value.encode("ascii", "ignore"))
        elif type(value) is dict:
            row.append(", ".join(value.values()))

    row_ascii = [v.encode("ascii", "ignore") for v in row]

    writer.writerow(row_ascii)
    # Return CSV file to browser as download
    return response


def export_entity_json(entity):
    # Return JS file to browser as download
    serialized = json.dumps(entity.to_dict())
    response = HttpResponse(serialized, mimetype='application/json')
    response['Content-Disposition'] = ('attachment; filename=%s.json'
                                       % slugify(entity))
    return response


class dict2xml(object):
    """ http://stackoverflow.com/questions/1019895/serialize-python-dictionary-to-xml """
    doc = Document()

    def __init__(self, structure):
        if len(structure) == 1:
            rootName = str(structure.keys()[0])
            self.root = self.doc.createElement(rootName)

            self.doc.appendChild(self.root)
            self.build(self.root, structure[rootName])

    def build(self, father, structure):
        if type(structure) == dict:
            for k in structure:
                tag = self.doc.createElement(k)
                father.appendChild(tag)
                self.build(tag, structure[k])

        elif type(structure) == list:
            grandFather = father.parentNode
            tagName = father.tagName
            grandFather.removeChild(father)
            for l in structure:
                tag = self.doc.createElement(tagName)
                self.build(tag, l)
                grandFather.appendChild(tag)
        else:
            if type(structure) == unicode:
                data = structure.encode("ascii", errors="xmlcharrefreplace")
            else:
                data = str(structure)
            tag = self.doc.createTextNode(data)
            father.appendChild(tag)

    def __str__(self):
        return self.doc.toprettyxml(indent=" ")


def export_entity_xml(entity):
    entity_xml = dict2xml({"Entity": entity.to_dict()})

    # Return XML file to browser as download
    response = HttpResponse(str(entity_xml), mimetype='application/xml')
    response['Content-Disposition'] = ('attachment; filename=%s.xml'
                                       % slugify(entity))
    return response


export_entity_modes = {
            'csv': export_entity_csv,
            'json': export_entity_json,
            'xml': export_entity_xml,
        }


def export_entity(mode, entity):
    if mode in export_entity_modes:
        return export_entity_modes[mode](entity)
    else:
        content = "Error 400, Format %s is not supported" % mode
        return HttpResponseBadRequest(content)
