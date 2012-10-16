from django.contrib import messages
from django.conf import settings
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse
from django.db.models.fields import FieldDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _


from met.metadataparser.decorators import user_can_edit
from met.metadataparser.models import Federation, Entity
from met.metadataparser.forms import (FederationForm, EntityForm,
                                      ServiceSearchForm)

from met.metadataparser.utils import export_query_set


def index(request):
    federations = Federation.objects.filter(is_interfederation=False)
    interfederations = Federation.objects.filter(is_interfederation=True)
    return render_to_response('metadataparser/index.html', {
           'interfederations': interfederations,
           'federations': federations,
           }, context_instance=RequestContext(request))


def federation_view(request, federation_id):
    federation = get_object_or_404(Federation, id=federation_id)
    entity_type = None
    if (request.GET and 'entity_type' in request.GET):
        entity_type = request.GET['entity_type']
        entities_id = federation._metadata.entities_by_type(entity_type)
        entities = Entity.objects.filter(entityid__in=entities_id)
    else:
        entities = Entity.objects.filter(federations__id=federation.id)

    return render_to_response('metadataparser/federation_view.html',
            {'federation': federation,
             'entity_type': entity_type or 'All',
             'entities': entities,
             'show_filters': True,
            }, context_instance=RequestContext(request))


@user_can_edit(Federation)
def federation_edit(request, federation_id=None):
    if federation_id is None:
        federation = None
    else:
        federation = get_object_or_404(Federation, id=federation_id)

    if request.method == 'POST':
        form = FederationForm(request.POST, request.FILES, instance=federation)
        if form.is_valid():
            form.save()
            if not federation:
                form.instance.editor_users.add(request.user)
            if 'file' in form.changed_data or 'file_url' in form.changed_data:
                form.instance.process_metadata()
                form.instance.process_metadata_entities()
            if federation:
                messages.success(request, _('Federation modified succesfully'))
            else:
                messages.success(request, _('Federation created succesfully'))

            federation = form.instance
            url = reverse('federation_view', args=[federation.id])
            return HttpResponseRedirect(url)

        else:
            messages.error(request, _('Please correct the errors indicated'
                                      ' below'))
    else:
        form = FederationForm(instance=federation)

    return render_to_response('metadataparser/federation_edit.html',
                              {'form': form},
                              context_instance=RequestContext(request))


@user_can_edit(Federation)
def federation_delete(request, federation_id):
    federation = get_object_or_404(Federation, id=federation_id)
    messages.success(request,
                     _(u"%(federation)s federation was deleted succesfully"
                     % {'federation': unicode(federation)}))
    federation.delete()
    return HttpResponseRedirect(reverse('federations_list'))


def entity_view(request, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)

    return render_to_response('metadataparser/entity_view.html',
            {'entity': entity,
            }, context_instance=RequestContext(request))


@user_can_edit(Entity)
def entity_edit(request, federation_id=None, entity_id=None):
    entity = None
    federation = None
    if federation_id:
        federation = get_object_or_404(Federation, id=federation_id)
        if entity_id:
            entity = get_object_or_404(Entity, id=entity_id,
                                       federations__id=federation.id)
    if entity_id and not federation_id:
        entity = get_object_or_404(Entity, id=entity_id)

    if request.method == 'POST':
        form = EntityForm(request.POST, request.FILES, instance=entity)
        if form.is_valid():
            form.save()
            if (federation and
               not federation in form.instance.federations.all()):
                form.instance.federations.add(federation)
                form.instance.save()
            if entity:
                messages.success(request, _('Entity modified succesfully'))
            else:
                messages.success(request, _('Entity created succesfully'))
            entity = form.instance
            url = reverse('entity_view', args=[entity.id])
            return HttpResponseRedirect(url)

        else:
            messages.error(request, _('Please correct the errors indicated'
                                      ' below'))
    else:
        form = EntityForm(instance=entity)

    return render_to_response('metadataparser/entity_edit.html',
                              {'form': form,
                               'federation': federation},
                              context_instance=RequestContext(request))


@user_can_edit(Entity)
def entity_delete(request, federation_id, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)
    messages.success(request,
                     _(u"%(entity)s entity was deleted succesfully"
                     % {'entity': unicode(entity)}))
    entity_id.delete()
    return HttpResponseRedirect(reverse('entities_list', args=[federation_id]))


## Querys
def search_service(request):
    entity_type = None
    if request.method == 'GET':
        if 'entityid' in request.GET:
            form = ServiceSearchForm(request.GET)
            if form.is_valid():
                entityid = form.cleaned_data['entityid']
                entityid = entityid.strip()
        else:
            form = ServiceSearchForm()
        entity_type = request.GET.get('entity_type', None)

    try:
        if entity_type:
            objects = Entity.longlist.filter(entityid__icontains=entityid,
                                            entity_type=entity_type)
        else:
            objects = Entity.objects.filter(entityid__icontains=entityid)
    except Entity.DoesNotExist:
        messages.info(request, _(u"Can't found %(entityid)s service"
                                   % {'entityid': entityid}))

    return render_to_response('metadataparser/service_search.html',
        {'searchform': form,
         'object_list': objects,
         'show_filters': False,
        }, context_instance=RequestContext(request))


def search_service_export(request, mode='json'):
    entity = None
    if request.method == 'GET' and 'entityid' in request.GET:
        form = ServiceSearchForm(request.GET)
        if form.is_valid():
            entityid = form.cleaned_data['entityid']
            try:
                entity = Entity.objects.get(entityid=entityid)
            except Entity.DoesNotExist:
                messages.info(request, _(u"Can't found %(entityid)s service"
                                         % {'entityid': entityid}))

        return export_query_set(mode, entity.federations.all(),
                                entity, ('name', 'url'))


def generic_list(request, objects, format, fields, headers, title, filename):
    model = objects.model
    headers = []
    for fieldname in fields:
        if fieldname:
            try:
                field = model._meta.get_field(fieldname)
                headers.append(field.verbose_name)
            except FieldDoesNotExist:
                if hasattr(objects[0], fieldname):
                    headers.append(fieldname.capitalize())
        else:
            headers.append(unicode(model._meta.verbose_name))

    if format:
        return export_query_set(format, objects, filename, fields)

    page = None
    if request.GET and 'page' in request.GET:
        page = request.GET['page']

    paginator = Paginator(objects, getattr(settings, 'PAGE_LENGTH', 25))

    try:
        objs_page = paginator.page(page)
    except PageNotAnInteger:
        objs_page = paginator.page(1)
    except EmptyPage:
        objs_page = paginator.page(paginator.num_pages)

    return render_to_response('metadataparser/generic_list.html',
                              {'objs_page': objs_page,
                               'objects': objects,
                               'headers': headers,
                               'fields': fields,
                               'title': title,
                              },
                              context_instance=RequestContext(request))
