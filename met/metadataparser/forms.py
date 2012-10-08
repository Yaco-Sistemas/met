from django import forms
from django.utils.translation import ugettext_lazy as _
from django.forms.widgets import CheckboxSelectMultiple

from met.metadataparser.models import Federation, Entity


class FederationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(FederationForm, self).__init__(*args, **kwargs)
        editor_users_choices = self.fields['editor_users'].widget.choices
        self.fields['editor_users'].widget = CheckboxSelectMultiple(
                                                choices=editor_users_choices)
        self.fields['editor_users'].help_text = _("This users can edit this "
                                                 "federation and his entities")

    def clean(self):
        cleaned_data = super(FederationForm, self).clean()
        file_url = cleaned_data.get("file_url")
        file = cleaned_data.get("file")
        if not (file or file_url):
            raise forms.ValidationError(_(u"Please, set a file or url to get "
                                       "metadata info."))
        return cleaned_data

    class Meta:
        model = Federation


class EntityForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(EntityForm, self).__init__(*args, **kwargs)
        federations_choices = self.fields['federations'].widget.choices
        self.fields['federations'].widget = CheckboxSelectMultiple(
                                                choices=federations_choices)
        self.fields['federations'].help_text = ''
        editor_users_choices = self.fields['editor_users'].widget.choices
        self.fields['editor_users'].widget = CheckboxSelectMultiple(
                                                choices=editor_users_choices)
        self.fields['editor_users'].help_text = _("This users can edit only "
                                                  "this entity")

    #def clean(self):
    #    cleaned_data = super(EntityForm, self).clean()
    #    file_url = cleaned_data.get("file_url")
    #    file = cleaned_data.get("file")
    #    federations = cleaned_data.get("federations")
    #    if not (file or file_url or federations):
    #        raise forms.ValidationError(_(u"Please, set a file, url or "
    #                                   "federation to get which has entity "
    #                                   "definition in his url metadata info."))
    #    return cleaned_data

    class Meta:
        model = Entity


class ServiceSearchForm(forms.Form):
    entityid = forms.CharField(max_length=200, label=_(u"Search service ID"),
                             help_text=_(u"Please, enter the exact entity id"),
                             widget=forms.TextInput(attrs={'size': '200'}))
