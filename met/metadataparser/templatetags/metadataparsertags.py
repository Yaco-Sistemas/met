from django import template
from met.metadataparser.models import Federation
from met.metadataparser.xmlparser import DESCRIPTOR_TYPES, DESCRIPTOR_TYPES_DISPLAY
from django.template.base import Node, TemplateSyntaxError
from urllib import urlencode

register = template.Library()


@register.inclusion_tag('metadataparser/bootstrap_form.html')
def bootstrap_form(form, cancel_link='..', delete_link=None):
    return {'form': form,
            'cancel_link': cancel_link,
            'delete_link': delete_link}


@register.inclusion_tag('metadataparser/bootstrap_searchform.html')
def bootstrap_searchform(form):
    return {'form': form}


@register.inclusion_tag('metadataparser/federations_summary_tag.html', takes_context=True)
def federations_summary(context, federations=None):
    if not federations:
        federations = Federation.objects.all()

    return {'federations': federations,
            'user': context.get('user', None),
            'entity_types': DESCRIPTOR_TYPES}


@register.inclusion_tag('metadataparser/tag_entity_filters.html', takes_context=True)
def entity_filters(context, entities):
    entity_types = ('All', ) + DESCRIPTOR_TYPES
    request = context.get('request')
    entity_type = request.GET.get('entity_type', '')
    rquery = request.GET.copy()
    for filter in ('entity_type', 'page'):
        if filter in rquery:
            rquery.pop(filter)
    if not entity_type:
        entity_type = 'All'
    query = urlencode(rquery)
    filter_base_path = request.path
    return {'filter_base_path': filter_base_path,
            'otherparams': query,
            'entity_types': entity_types,
            'entity_type': entity_type,
            'entities': entities}


@register.simple_tag()
def entity_filter_url(base_path, filter, otherparams=None):
    url = base_path
    if filter != 'All':
        url += '?entity_type=%s' % filter
        if otherparams:
            url += '&%s' % otherparams
    elif otherparams:
        url += '?%s' % otherparams

    return url


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
        return '<a href="%(link)s">%(name)s</a>' % {"link": obj.get_absolute_url(),
                                                    "name": unicode(obj),
                                                    }
    if isinstance(obj, dict):
        return obj.get(prop, None)
    if getattr(getattr(obj, uprop, None), 'all', None):

        return '. '.join(['<a href="%(link)s">%(name)s</a>' % {"link": item.get_absolute_url(),
                                                    "name": unicode(item)}
                          for item in getattr(obj, uprop).all()])
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


@register.filter(name='wrap')
def wrap(value, length):
    value = unicode(value)
    if len(value) > length:
        return "%s..." % value[:length]
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
