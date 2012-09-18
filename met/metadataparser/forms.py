from django import forms

from met.metadataparser.models import Metadata, Federation, Entity


class MetadataForm(forms.ModelForm):

    class Meta:
        model=Metadata


class FederationForm(forms.ModelForm):

    class Meta:
        model=Federation


class EntityForm(forms.ModelForm):

    class Meta:
        model=Entity
