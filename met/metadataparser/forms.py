from django import forms

from met.metadataparser.models import Federation, Entity


class FederationForm(forms.ModelForm):

    class Meta:
        model = Federation


class EntityForm(forms.ModelForm):

    class Meta:
        model = Entity
