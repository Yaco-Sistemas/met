import csv
from django.http import HttpResponse, HttpResponseBadRequest
from django.template.defaultfilters import slugify
import django.utils.simplejson as json
from xml.dom.minidom import Document
import hashlib


## Taken from http://djangosnippets.org/snippets/790/
def export_csv(qs, filename, fields=None):
    model = qs.model
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = ('attachment; filename=%s.csv'
                                       % slugify(filename))
    writer = csv.writer(response)
    # Write headers to CSV file
    if fields:
        headers = fields
    else:
        headers = []
        for field in model._meta.fields:
            headers.append(field.name)
        fields = headers
    _headers = []
    for header in headers:
        if header:
            _headers.append(header)
        else:
            _headers.append(unicode(model._meta.verbose_name))

    headers = _headers

    writer.writerow(headers)
    # Write data to CSV file
    for obj in qs:
        row = []
        for field in fields:
            if field == '':
                val = unicode(obj)
            else:
                val = getattr(obj, field)
                if callable(val):
                    val = val()
                elif getattr(val, 'all', None):
                    val = ', '.join([unicode(item) for item in val.all()])
                # work around csv unicode limitation
                elif type(val) == unicode:
                    val = val.encode("utf-8")
            row.append(val)
        writer.writerow(row)
    # Return CSV file to browser as download
    return response


def export_json(qs, filename, fields=None):
    model = qs.model

    # Write headers to CSV file
    if not fields:
        headers = []
        for field in model._meta.fields:
            headers.append(field.name)
        fields = headers
    objs = []
    for obj in qs:
        item = {}
        for field in fields:
            if field == '':
                field = unicode(obj._meta.verbose_name)
                val = unicode(obj)
            else:
                val = getattr(obj, field)
                if callable(val):
                    val = val()
                elif getattr(val, 'all', None):
                    val = [unicode(i) for i in val.all()]
                # work around csv unicode limitation
                elif type(val) == unicode:
                    val = val.encode("utf-8")
            item[field] = val
        objs.append(item)
    # Return JS file to browser as download
    serialized = json.dumps(objs)
    response = HttpResponse(serialized, mimetype='application/json')
    response['Content-Disposition'] = ('attachment; filename=%s.json'
                                       % slugify(filename))
    return response


def export_xml(qs, filename, fields=None):
    model = qs.model
    xml = Document()
    root = xml.createElement(filename)
    xml.appendChild(root)
    # Write headers to CSV file
    if not fields:
        headers = []
        for field in model._meta.fields:
            headers.append(field.name)
        fields = headers
    for obj in qs:
        item = xml.createElement(model._meta.object_name)
        item.setAttribute("id", unicode(obj))
        for field in fields:
            if field != '':
                val = getattr(obj, field)
                if getattr(val, 'all', None):
                    for v in val.all():
                        element = xml.createElement(field)
                        xmlval = xml.createTextNode(unicode(v))
                        element.appendChild(xmlval)
                        item.appendChild(element)
                else:
                    if callable(val):
                        val = val()
                    # work around csv unicode limitation
                    elif type(val) == unicode:
                        val = val.encode("utf-8")

                    element = xml.createElement(field)
                    xmlval = xml.createTextNode(val)
                    element.appendChild(xmlval)
                    item.appendChild(element)
        root.appendChild(item)
    # Return xml file to browser as download
    response = HttpResponse(xml.toxml(), mimetype='application/xml')
    response['Content-Disposition'] = ('attachment; filename=%s.xml'
                                       % slugify(filename))
    return response


export_modes = {
            'csv': export_csv,
            'json': export_json,
            'xml': export_xml,
        }


def export_query_set(mode, qs, filename, fields=None):
    if mode in export_modes:
        return export_modes[mode](qs, filename, fields)
    else:
        content = "Error 400, Format %s is not supported" % mode
        return HttpResponseBadRequest(content)


def compare_filecontents(a, b):
    md5_a = hashlib.md5(a).hexdigest()
    md5_b = hashlib.md5(b).hexdigest()
    return (md5_a == md5_b)
