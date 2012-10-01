from django import template
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.conf import settings

from met.metadataparser.models import Federation
from met.metadataparser.xmlparser import DESCRIPTOR_TYPES

register = template.Library()


@register.inclusion_tag('metadataparser/bootstrap_form.html')
def bootstrap_form(form, cancel_link='..', delete_link=None):
    return {'form': form,
            'cancel_link': cancel_link,
            'delete_link': delete_link}


@register.inclusion_tag('metadataparser/bootstrap_searchform.html')
def bootstrap_searchform(form):
    return {'form': form}


@register.inclusion_tag('metadataparser/tag_entities_list.html')
def federation_entities_list(federation, entities, page, entity_type=None):

    paginator = Paginator(entities, getattr(settings, 'PAGE_LENGTH', 25))

    try:
        entities_page = paginator.page(page)
    except PageNotAnInteger:
        entities_page = paginator.page(1)
    except EmptyPage:
        entities_page = paginator.page(paginator.num_pages)

    if entity_type and entity_type != 'All':
        append_url = '&entity_type=%s' % entity_type
    else:
        append_url = ''

    return {'federation': federation,
            'entity_type': entity_type,
            'append_url': append_url,
            'entities': entities_page}


@register.inclusion_tag('metadataparser/federations_summary_tag.html')
def federations_summary(federations=None, page=1):
    if not federations:
        federations = Federation.objects.all()

    paginator = Paginator(federations, getattr(settings, 'PAGE_LENGTH', 25))

    try:
        federations_page = paginator.page(page)
    except PageNotAnInteger:
        federations_page = paginator.page(1)
    except EmptyPage:
        federations_page = paginator.page(paginator.num_pages)

    return {'federations': federations_page,
            'entity_types': DESCRIPTOR_TYPES}


@register.simple_tag()
def entities_count(federation, entity_type=None):
    if entity_type and entity_type != 'All':
        return federation._metadata.count_entities_by_type(entity_type)
    else:
        return federation._metadata.count_entities()


@register.simple_tag(takes_context=True)
def l10n_property(context, prop):
    if isinstance(prop, dict):
        lang = context.get('LANGUAGE_CODE', None)
        if lang and lang in prop:
            return prop.get(lang)
        else:
            return prop[prop.keys()[0]]
    return prop


@register.simple_tag()
def get_property(obj, prop=None):
    if not unicode(prop):
        return unicode(obj)
    return getattr(obj, unicode(prop), '')
