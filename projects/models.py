# Django imports
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.safestring import mark_safe
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator, FileExtensionValidator

# Project imports
from PIL import Image as Im

# Create your models here.
# Test of image integration
"""
class Image(models.Model):
    name = models.CharField(max_length=20)
    photo = models.ImageField(upload_to='profile_img')

    def __str__(self):
        return self.name

    def image_tag(self):
        return mark_safe(f'<img src="/../../media/{self.photo}" width="150" height="150" />')

    def save(self):
        super().save()
        img = Im.open(self.photo.path)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.photo.path)
"""
# PATH for files of User model
def user_dir_path(instance, filename):
    return f'user_{instance.username}/{filename}'

class User(AbstractUser):
    description = models.TextField(max_length=512, blank=True)
    career = models.CharField(max_length=64)
    instagram = models.URLField(blank=True)
    profile_img = models.ImageField(upload_to=user_dir_path, default='assets/an_user.png')
    banner = models.ImageField(upload_to=user_dir_path, blank=True)
    curriculum = models.FileField(upload_to=user_dir_path, blank=True, validators=[FileExtensionValidator(['pdf','docx'])])
    skills = models.ManyToManyField('Skill', blank=True)

    def __str__(self):
        return self.username

    def serialize(self):
        return {
            'id': self.id,
            'name': self.username,
            'career': self.career
        }

class Category(models.Model):
    name = models.CharField(max_length=64)
    name_en = models.CharField(max_length=64, blank=True)

    def __str__(self):
        return self.name

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'name_en': self.name_en
        }

def project_dir_path(instance, filename):
    return f'projects/{instance.title}/{filename}'
    
class Project(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=512, blank=True)
    progress = models.IntegerField(default=0, validators=[MaxValueValidator(100), MinValueValidator(0)])
    pub_date = models.DateTimeField(default=timezone.now)
    image = models.ImageField(upload_to=project_dir_path, default='assets/yard.bmp')
    public = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.DO_NOTHING, editable=False, related_name='owner_project')
    members = models.ManyToManyField(User, related_name='my_projects')
    categories = models.ManyToManyField(Category, blank=True, related_name='projects')

    def __str__(self):
        return self.title

    def members_list(self):
        return [user for user in self.members.all() if not user.is_superuser]

    def form(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'progress': self.progress,
            'image': self.image,
            'members': self.members_list(),
            'pub_date': self.pub_date,
            'public': self.public,
            'categories': self.categories.first()
        }
        
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'progress': self.progress,
            'image': self.image.url,
            'owner': self.owner.username,
            'members': [user.serialize() for user in self.members.all() if not user.is_superuser],
            'pub_date': self.pub_date,
            'public': self.public,
            'categories': [cat.serialize() for cat in self.categories.all()]
        }

class Skill(models.Model):
    name = models.CharField(max_length=64)
    name_en = models.CharField(max_length=64, blank=True)
    icon = models.FileField(upload_to='icon_skills')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="skills")

    def __str__(self):
        return self.name

    def icon_tag(self):
        return mark_safe(f'<img src="/../../media/{self.icon}" width="44" height="44" />')

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'name_en': self.name_en,
            'icon': self.icon.path,
            'category': self.category
        }

class Comment(models.Model):
    content = models.TextField(max_length=256)
    pub_date = models.DateTimeField(default=timezone.now)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='comments')

    def __str__(self):
        return f'{self.owner} comment in {self.project}'
