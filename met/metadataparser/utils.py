import csv
from django.http import HttpResponse, HttpResponseBadRequest
from django.template.defaultfilters import slugify
import django.utils.simplejson as json


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
    writer.writerow(headers)
    # Write data to CSV file
    for obj in qs:
        row = []
        for field in headers:
            if field in headers:
                val = getattr(obj, field)
                if callable(val):
                    val = val()
                # work around csv unicode limitation
                if type(val) == unicode:
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
    objs = []
    for obj in qs:
        item = {}
        for field in fields:
            if field in fields:
                val = getattr(obj, field)
                if callable(val):
                    val = val()
                # work around csv unicode limitation
                if type(val) == unicode:
                    val = val.encode("utf-8")
                item[field] = val
        objs.append(item)
    # Return JS file to browser as download
    serialized = json.dumps(objs)
    response = HttpResponse(serialized, mimetype='application/json')
    response['Content-Disposition'] = ('attachment; filename=%s.json'
                                       % slugify(filename))
    return response


export_modes = {
            'json': export_json,
            'csv': export_csv,
        }


def export_query_set(mode, qs, filename, fields=None):
    if mode in export_modes:
        return export_modes[mode](qs, filename, fields)
    else:
        return HttpResponseBadRequest()
