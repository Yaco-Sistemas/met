from django import template
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.conf import settings
from met.metadataparser.models import Federation
from met.metadataparser.xmlparser import DESCRIPTOR_TYPES, DESCRIPTOR_TYPES_DISPLAY
from django.template.base import Node, TemplateSyntaxError

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


@register.inclusion_tag('metadataparser/tag_paginator.html')
def paginator(objects):
    ratio = 2
    pages = objects.paginator.num_pages
    cpage = objects.number
    if (cpage - ratio) > 1:
        pmin = cpage - ratio
    else:
        pmin = 1
    if (cpage + ratio) < pages:
        pmax = cpage + ratio
    else:
        pmax = objects.paginator.num_pages
    pages = range(pmin, pmax + 1)
    return {'objs': objects,
            'pages': pages}


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
    uprop = unicode(prop)
    if not uprop:
        return unicode(obj)
    if isinstance(obj, dict):
        return obj.get(prop, None)
    if getattr(getattr(obj, uprop, None), 'all', None):
        return ', '.join([unicode(item) for item in getattr(obj, uprop).all()])
    if isinstance(getattr(obj, uprop, ''), list):
        return ', '.join(getattr(obj, uprop, []))
    return getattr(obj, uprop, '')


@register.simple_tag(takes_context=True)
def active_url(context, pattern):
    request = context.get('request')
    if request.path == pattern:
        return 'active'
    return ''


@register.filter(name='display_etype')
def display_etype(value, separator=', '):
    if isinstance(value, list):
        display = []
        for item in value:
            if item in DESCRIPTOR_TYPES_DISPLAY:
                display.append(DESCRIPTOR_TYPES_DISPLAY.get(item))
            else:
                display.append(item)
        return separator.join(display)
    else:
        if value in DESCRIPTOR_TYPES_DISPLAY:
            return DESCRIPTOR_TYPES_DISPLAY.get(value)
        else:
            return value


class CanEdit(Node):
    child_nodelists = ('nodelist')

    def __init__(self, obj, nodelist):
        self.obj = obj
        self.nodelist = nodelist

    def __repr__(self):
        return "<CanEdit>"

    def render(self, context):
        obj = self.obj.resolve(context, True)
        user = context.get('user')
        if obj.can_edit(user):
            return self.nodelist.render(context)
        else:
            return ''


def do_canedit(parser, token):
    bits = list(token.split_contents())
    if len(bits) != 2:
        raise TemplateSyntaxError("%r takes 1 argument" % bits[0])
    end_tag = 'end' + bits[0]
    nodelist = parser.parse((end_tag,))
    obj = parser.compile_filter(bits[1])
    token = parser.next_token()
    return CanEdit(obj, nodelist)


@register.tag
def canedit(parser, token):
    """
    Outputs the contents of the block if user has edit pemission

    Examples::

        {% canedit obj %}
            ...
        {% endcanedit %}
    """
    return do_canedit(parser, token)
