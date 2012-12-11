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
    labels = ['name']
    labels.extend([label for (label, ff) in counters])
    writer.writerow(labels)
    # Write data to CSV file
    for obj in qs:
        row = [unicode(obj)]
        for (counter_label, counter_filter) in counters:
            row.append(getattr(obj, relation).filter(**counter_filter).count())
        writer.writerow(row)
    # Return CSV file to browser as download
    return response


def export_entity_json(qs, relation, filename, counters=None):
    objs = {}
    for obj in qs:
        item = {}
        for (counter_label, counter_filter) in counters:
            item[counter_label] = getattr(obj, relation).filter(**counter_filter).count()
        objs[unicode(obj)] = item
    # Return JS file to browser as download
    serialized = json.dumps(objs)
    response = HttpResponse(serialized, mimetype='application/json')
    response['Content-Disposition'] = ('attachment; filename=%s.json'
                                       % slugify(entity))
    return response


def export_entity_xml(qs, relation, filename, counters):
    model = qs.model

    xml = Document()
    root = xml.createElement(filename)
    xml.appendChild(root)
    # Write data to CSV file
    for obj in qs:
        item = xml.createElement(model._meta.object_name)
        item.setAttribute("id", unicode(obj))
        for (counter_label, counter_filter) in counters:
            val = getattr(obj, relation).filter(**counter_filter).count()
            element = xml.createElement(counter_label)
            xmlval = xml.createTextNode(unicode(val))
            element.appendChild(xmlval)
            item.appendChild(element)

        root.appendChild(item)

    # Return XML file to browser as download
    response = HttpResponse(xml.toxml(), mimetype='application/xml')
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
