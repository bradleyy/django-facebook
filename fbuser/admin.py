from django.contrib import admin
from fbuser.models import FBUser

class FBUserAdmin(admin.ModelAdmin):
	list_display = ('user', 'uid', 'name',)

admin.site.register(FBUser, FBUserAdmin)

