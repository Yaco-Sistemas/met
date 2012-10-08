from met.metadataparser.forms import ServiceSearchForm


def nav_search_form(request):
    searchform = ServiceSearchForm(request.GET)
    return {'nav_searchform': searchform}
