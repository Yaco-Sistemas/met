from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _


from met.metadataparser.models import Metadata, Federation, Entity
from met.metadataparser.forms import MetadataForm, FederationForm, EntityForm


def metadatas_list(request):
    metadatas = Metadata.objects.all()

    return render_to_response('metadataparser/metadatas_list.html', {
           'metadatas': metadatas,
           }, context_instance=RequestContext(request))


def metadata_view(request, metadata_id):
    metadata = get_object_or_404(Metadata, id=metadata_id)
    return render_to_response('metadataparser/metadata_view.html',
            {'metadata': metadata,
            }, context_instance=RequestContext(request))


def metadata_edit(request, metadata_id=None):
    if metadata_id is None:
        metadata = None
    else:
        metadata = get_object_or_404(Metadata, id=metadata_id)

    if request.method == 'POST':
        form = MetadataForm(request.POST, request.FILES, instance=metadata)
        if form.is_valid():
            form.save()
            messages.success(request, _('Metadata created succesfully'))
            metadata = form.instance
            url = reverse('metadata_view', args=[metadata.id])
            return HttpResponseRedirect(url)

        else:
            messages.error(request, _('Please correct the errors indicated'
                                      ' below'))
    else:
        form = MetadataForm(instance=metadata)

    return render_to_response('metadataparser/metadata_edit.html',
                              {'form': form},
                              context_instance=RequestContext(request))


def metadata_delete(request, metadata_id):
    metadata = get_object_or_404(Metadata, id=metadata_id)
    messages.success(request,
                     _(u"%(metadata)s metadata was deleted succesfully"
                     % {'metadata': unicode(metadata)}))
    metadata.delete()
    return HttpResponseRedirect('metadatas_list')


def federations_list(request):
    federations = Federation.objects.all()

    return render_to_response('metadataparser/federations_list.html', {
           'federations': federations,
           }, context_instance=RequestContext(request))


def federation_view(request, federation_id):
    federation = get_object_or_404(Federation, id=federation_id)
    return render_to_response('metadataparser/federation_view.html',
            {'federation': federation,
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


def entities_list(request, federation_id):
    entities = Entity.objects.all()
    federation = get_object_or_404(Federation, id=federation_id)
    return render_to_response('metadataparser/entities_list.html', {
           'federation': federation,
           'entities': entities,
           }, context_instance=RequestContext(request))


def entity_view(request, federation_id, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)
    federation = get_object_or_404(Federation, id=federation_id)
    return render_to_response('metadataparser/entity_view.html',
            {'federation': federation,
             'entity': entity,
            }, context_instance=RequestContext(request))


def entity_edit(request, federation_id, entity_id=None):
    if entity_id is None:
        entity = None
    else:
        entity = get_object_or_404(Entity, id=entity_id)
    federation = get_object_or_404(Federation, id=federation_id)

    if request.method == 'POST':
        form = EntityForm(request.POST, request.FILES, instance=entity)
        if form.is_valid():
            form.save()
            form.instance.federation = federation
            form.instance.save()
            messages.success(request, _('Federation created succesfully'))
            entity = form.instance
            url = reverse('entity_view', args=[federation.id, entity.id])
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
