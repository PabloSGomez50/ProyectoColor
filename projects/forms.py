# Django imports
from django import forms

# Proyect imports
from .models import Image

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['name', 'photo']