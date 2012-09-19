from django import template


register = template.Library()


@register.inclusion_tag('metadataparser/bootstrap_form.html')
def bootstrap_form(form, cancel_link, delete_link=None):
    return {'form': form,
            'cancel_link': cancel_link,
            'delete_link': delete_link}
