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

    class Meta:
        model = Entity


class ServiceSearchForm(forms.Form):
    entityid = forms.CharField(max_length=200, label=_(u"Search service ID"),
                             help_text=_(u"Enter a full or partial entityid"),
                             widget=forms.TextInput(attrs={'size': '200'}))
