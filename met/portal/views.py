from django.shortcuts import render_to_response
from django.template import RequestContext

from met.metadataparser.models import Metadata

def index(request):

    return render_to_response('portal/index.html', {
           }, context_instance=RequestContext(request))
