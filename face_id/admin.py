from django.contrib import admin
from .models import Profile, Shift, Attendance, Leave
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
# Register your models here.

class ProfileInline(admin.StackedInline):
  model = Profile
  can_delete = False
  
class CustomUserAdmin(UserAdmin):
  inlines = (ProfileInline,)
  
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Shift)
admin.site.register(Attendance)
admin.site.register(Leave)