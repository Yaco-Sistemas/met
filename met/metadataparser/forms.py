from django import forms

from met.metadataparser.models import Metadata


class MetadataForm(forms.ModelForm):

    class Meta:
        model=Metadata
