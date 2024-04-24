from django.contrib import admin

from core import models

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
#TRANSLATE SOMETHING WITH _
from django.utils.translation import gettext_lazy as _

class UserAdmin(BaseUserAdmin):
#Needs to support all the custom fields
#The django class excepts a user name which is not provided
#so custom fieldsets needs to be provided here

#Click on the admin@admin.com to view this page
    ordering = ['id']
    list_display = ['email', 'name']
    #fields that has been created or from the Mixin Class
    fieldsets = (
        #None is instead of a title
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('name',)}),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                )
            }
        ),
        (_('Important dates test blabla'), {'fields': ('last_login',)}),
    )

    readonly_fields = ['last_login']

    #add user fields
    add_fieldsets = (
        (None, {
            #wide is to make the layout of the page more wide
            'classes': ('wide',),
            'fields': (
                'email',
                'password1',
                'password2',
                'name',
                'is_active',
                'is_staff',
                'is_superuser',
            ),
        }),
    )

#UserAdmin is optional if left it will use default admin model manager
# And would not display any of the changes in made in this class
admin.site.register(models.User, UserAdmin)
admin.site.register(models.Recipe)
admin.site.register(models.Tag)
admin.site.register(models.Ingredient)