from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _


from met.metadataparser.models import Federation, Entity
from met.metadataparser.forms import (FederationForm, EntityForm,
                                      ServiceSearchForm)


def federations_list(request):
    federations = Federation.objects.all()

    return render_to_response('metadataparser/federations_list.html', {
           'federations': federations,
           }, context_instance=RequestContext(request))


def federation_view(request, federation_id):
    federation = get_object_or_404(Federation, id=federation_id)
    entity_type = None
    if (request.GET and 'entity_type' in request.GET):
        entity_type = request.GET['entity_type']
        entities = federation.entity_set.filter(entity_type=entity_type)
    else:
        entities = federation.entity_set.all()

    page = None
    if request.GET and 'page' in request.GET:
        page = request.GET['page']

    return render_to_response('metadataparser/federation_view.html',
            {'federation': federation,
             'entity_type': entity_type,
             'entities': entities,
             'page': page or 1,
            }, context_instance=RequestContext(request))


def federation_edit(request, federation_id=None):
    if federation_id is None:
        federation = None
    else:
        federation = get_object_or_404(Federation, id=federation_id)

    if request.method == 'POST':
        form = FederationForm(request.POST, request.FILES, instance=federation)
        if form.is_valid():
            form.save()
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


def federation_delete(request, federation_id):
    federation = get_object_or_404(Federation, id=federation_id)
    messages.success(request,
                     _(u"%(federation)s federation was deleted succesfully"
                     % {'federation': unicode(federation)}))
    federation.delete()
    return HttpResponseRedirect('federations_list')


def entity_view(request, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)
    return render_to_response('metadataparser/entity_view.html',
            {'entity': entity,
            }, context_instance=RequestContext(request))


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


def entity_delete(request, federation_id, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)
    messages.success(request,
                     _(u"%(entity)s entity was deleted succesfully"
                     % {'entity': unicode(entity)}))
    entity_id.delete()
    return HttpResponseRedirect('entities_list', args=[federation_id])


## Querys
def search_service(request):
    entity = None
    if request.method == 'POST':
        form = ServiceSearchForm(request.POST)
        if form.is_valid():
            entityid = form.cleaned_data['entityid']
            try:
                entity = Entity.objects.get(entityid=entityid)
            except Entity.DoesNotExist:
                messages.info(request, _(u"Can't found %(entityid)s service"
                                         % {'entityid': entityid}))

    else:
            form = ServiceSearchForm()
    return render_to_response('metadataparser/service_search.html',

            {'searchform': form,
             'entity': entity,
            }, context_instance=RequestContext(request))
