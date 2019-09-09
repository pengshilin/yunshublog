from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile

class ProfileInline(admin.StackedInline):
    '''定义一个行内admin'''
    model = Profile
    can_delete = False
    verbose_name_plural = 'UserProfile'

class UserAdmin(BaseUserAdmin):
    '''将Profile关联到User中'''
    inlines = (ProfileInline,)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)