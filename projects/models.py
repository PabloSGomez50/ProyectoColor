# Django imports
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.safestring import mark_safe
from django.utils import timezone

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
    curriculum = models.FileField(upload_to=user_dir_path, blank=True)
    skills = models.ManyToManyField('Skill', blank=True)

    def __str__(self):
        return self.username

    def serialize(self):
        return {
            'name': self.username
        }

class Category(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name

def project_dir_path(instance, filename):
    return f'projects/{instance.title}/{filename}'
    
class Project(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=512, blank=True)
    progress = models.PositiveSmallIntegerField(default=0)
    pub_date = models.DateTimeField(default=timezone.now)
    image = models.ImageField(upload_to=project_dir_path, default='assets/yard.bmp')
    public = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='owner_project')
    members = models.ManyToManyField(User, related_name='my_projects')
    categories = models.ManyToManyField(Category, blank=True, related_name='projects')

    def __str__(self):
        return self.title

    def members_list(self):
        return [x.username for x in self.members.all()]

    def serialize(self):
        return {
            'title': self.title,
            'image': self.image.url,
            'members': [x.username for x in self.members.all()],
            'public': self.public
        }

class Skill(models.Model):
    name = models.CharField(max_length=64)
    icon = models.FileField(upload_to='icon_skills')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="skills")

    def __str__(self):
        return self.name

    def icon_tag(self):
        return mark_safe(f'<img src="/../../media/{self.icon}" width="44" height="44" />')

class Comment(models.Model):
    content = models.TextField(max_length=256)
    pub_date = models.DateTimeField(default=timezone.now)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='comments')

    def __str__(self):
        return f'{self.owner} comment in {self.project}'
