from django import forms
from django.utils.translation import ugettext_lazy as _
from django.forms.widgets import CheckboxSelectMultiple

from met.metadataparser.models import Federation, Entity


class FederationForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super(FederationForm, self).clean()
        file_url = cleaned_data.get("file_url")
        file = cleaned_data.get("file")
        if not (file or file_url):
            raise forms.ValidationError(_("Please, set a file or url to get "
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

    def clean(self):
        cleaned_data = super(EntityForm, self).clean()
        file_url = cleaned_data.get("file_url")
        file = cleaned_data.get("file")
        federations = cleaned_data.get("federations")
        if not (file or file_url or federations):
            raise forms.ValidationError(_("Please, set a file, url or "
                                       "federation to get which has entity "
                                       "definition in his url metadata info."))
        return cleaned_data

    class Meta:
        model = Entity
