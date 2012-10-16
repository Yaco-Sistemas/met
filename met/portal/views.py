from django.shortcuts import render_to_response
from django.template import RequestContext


def error403(request):
    return render_to_response('403.html', {
           }, context_instance=RequestContext(request))


def error404(request):
    return render_to_response('404.html', {
           }, context_instance=RequestContext(request))


def error500(request):
    return render_to_response('500.html', {
           }, context_instance=RequestContext(request))
