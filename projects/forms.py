# Django imports
from django.forms import ModelForm

# Proyect imports
from .models import User, Project, Comment
"""
class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['name', 'photo']
"""

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = '__all__'

class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = '__all__'

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = '__all__'