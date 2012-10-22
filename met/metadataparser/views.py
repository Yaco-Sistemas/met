from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _


from met.metadataparser.decorators import user_can_edit
from met.metadataparser.models import Federation, Entity
from met.metadataparser.forms import (FederationForm, EntityForm,
                                      ServiceSearchForm)

from met.metadataparser.summary_export import export_summary
from met.metadataparser.query_export import export_query_set
from met.metadataparser.xmlparser import DESCRIPTOR_TYPES


def index(request):
    federations = Federation.objects.filter(is_interfederation=False)

    interfederations = Federation.objects.filter(is_interfederation=True)
    export = request.GET.get('export', None)
    format = request.GET.get('format', None)
    if export and format:
        counters = (
                    ('all', {}),
                    ('IDPSSO', {'types__xmlname': 'IDPSSODescriptor'}),
                    ('SPSSO', {'types__xmlname': 'SPSSODescriptor'}),
                   )
        if export == 'interfederations':
            return export_summary(request.GET.get('format'), interfederations,
                                  'entity_set', 'interfederations_summary',
                                  counters)

        elif export == 'federations':
            return export_summary(request.GET.get('format'), federations,
                                  'entity_set', 'federations_summary',
                                  counters)
        else:
            raise HttpResponseBadRequest('Not valid export query')

    return render_to_response('metadataparser/index.html', {
           'interfederations': interfederations,
           'federations': federations,
           'entities': Entity.objects.all(),
           'entity_types': DESCRIPTOR_TYPES,
           }, context_instance=RequestContext(request))


def federation_view(request, federation_slug=None):
    federation = get_object_or_404(Federation, slug=federation_slug)

    entity_type = None
    if (request.GET and 'entity_type' in request.GET):
        entity_type = request.GET['entity_type']
        entities_id = federation._metadata.entities_by_type(entity_type)
        entities = Entity.objects.filter(entityid__in=entities_id)
    else:
        entities = Entity.objects.filter(federations__id=federation.id)

    if 'format' in request.GET:
        return export_query_set(request.GET.get('format'), entities,
                                'entities_search_result', ('', 'types', 'federations'))
    return render_to_response('metadataparser/federation_view.html',
            {'federation': federation,
             'entity_type': entity_type or 'All',
             'entities': entities,
             'show_filters': True,
            }, context_instance=RequestContext(request))


@user_can_edit(Federation)
def federation_edit(request, federation_slug=None):
    if federation_slug is None:
        federation = None
    else:
        federation = get_object_or_404(Federation, slug=federation_slug)

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

            return HttpResponseRedirect(form.instance.get_absolute_url())

        else:
            messages.error(request, _('Please correct the errors indicated'
                                      ' below'))
    else:
        form = FederationForm(instance=federation)

    return render_to_response('metadataparser/federation_edit.html',
                              {'form': form},
                              context_instance=RequestContext(request))


@user_can_edit(Federation)
def federation_delete(request, federation_slug):
    federation = get_object_or_404(Federation, slug=federation_slug)
    messages.success(request,
                     _(u"%(federation)s federation was deleted succesfully"
                     % {'federation': unicode(federation)}))
    federation.delete()
    return HttpResponseRedirect(reverse('index'))


def entity_view(request, entityid):
    entity = get_object_or_404(Entity, entityid=entityid)

    return render_to_response('metadataparser/entity_view.html',
            {'entity': entity,
            }, context_instance=RequestContext(request))


@user_can_edit(Entity)
def entity_edit(request, federation_slug=None, entity_id=None):
    entity = None
    federation = None
    if federation_slug:
        federation = get_object_or_404(Federation, slug=federation_slug)
        if entity_id:
            entity = get_object_or_404(Entity, id=entity_id,
                                       federations__id=federation.id)
    if entity_id and not federation_slug:
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
            return HttpResponseRedirect(form.instance.get_absolute_url())

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
def entity_delete(request, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)
    messages.success(request,
                     _(u"%(entity)s entity was deleted succesfully"
                     % {'entity': unicode(entity)}))
    entity.delete()
    return HttpResponseRedirect(reverse('index'))


## Querys
def search_service(request):
    filters = {}
    objects = []
    if request.method == 'GET':
        if 'entityid' in request.GET:
            form = ServiceSearchForm(request.GET)
            if form.is_valid():
                entityid = form.cleaned_data['entityid']
                entityid = entityid.strip()
                filters['entityid__icontains'] = entityid

        else:
            form = ServiceSearchForm()
        entity_type = request.GET.get('entity_type', None)
        if entity_type:
            filters['entity_type'] = entity_type
        if filters:
            objects = Entity.objects.filter(**filters)

    if objects and 'format' in request.GET:
        return export_query_set(request.GET.get('format'), objects,
                                'entities_search_result', ('', 'types', 'federations'))

    return render_to_response('metadataparser/service_search.html',
        {'searchform': form,
         'object_list': objects,
         'show_filters': False,
        }, context_instance=RequestContext(request))
