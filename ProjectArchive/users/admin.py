from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import AuthUser, Student, HOD


class AuthUserAdminConfig(UserAdmin):

	model = AuthUser
	list_display = ('username', 'first_name', 'last_name', 'status')
	add_fieldsets = (
	 	(None, 
	 		{
				'classes': ('wide',),
	 			'fields': ('username', 'first_name', 'last_name', 'password1', 'password2')
	 		}
	 	),	
	 )
	ordering = ('username',)
	fieldsets = (
		(None, {'fields': ('username', 'first_name', 'last_name', 'password', 'status', 'is_student', 'is_hod')}),
    )
admin.site.register(AuthUser, AuthUserAdminConfig)


class StudentAdminConfig(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'gender', 'faculty',
                    'department', 'programme', 'session')
    # search_fields = ('username', 'first_name', 'last_name')
    # list_filter = ('gender', 'faculty', 'department', 'programme', 'session')
    ordering = ('last_name', 'first_name')
    
    add_fieldsets = (
	 	(None, 
	 		{
				'classes': ('wide',),
	 			'fields': ('gender', 'faculty', 'department', 'programme', 'session')
	 		}
	 	),	
	 )
admin.site.register(Student, StudentAdminConfig)


class HODAdminConfig(admin.ModelAdmin):
    add_fieldsets = (
	 	(None, 
	 		{
				'classes': ('wide',),
	 			'fields': ('faculty', 'department')
	 		}
	 	),	
	 )
admin.site.register(HOD, HODAdminConfig)