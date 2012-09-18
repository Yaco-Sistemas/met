from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _


from met.metadataparser.models import Metadata
from met.metadataparser.forms import MetadataForm


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
            form.instance.owner = request.user
            form.instance.save()
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
