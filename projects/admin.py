# Django imports
from django.contrib import admin

# Project imports
from .models import User, Project, Category, Skill, SkillGroup, Comment, SocialIcon, SocialMedia

"""
class ImageAdmin(admin.ModelAdmin):
    list_display = ['name','image_tag','photo']

admin.site.register(Image, ImageAdmin)
"""
# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'career']

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'members_list', 'pub_date', 'owner']
    date_hierarchy = 'pub_date'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'owner', 'project']

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'icon_tag']

@admin.register(SkillGroup)
class SkillGroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'user'] # , 'skills'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']

@admin.register(SocialIcon)
class SocialIconAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'icon_tag']

@admin.register(SocialMedia)
class SocialMediaAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'site', 'url']