from django.contrib import admin
from .models import *
# Register your models here.

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_name', 'created_on', 'active']
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'join_date', 'is_delete', 'phone_number']

@admin.register(GlobalConfiguration)
class GlobalConfigurationAdmin(admin.ModelAdmin):
    list_display = ['name', 'value']

@admin.register(GuardianDetails)
class GuardianDetailsAdmin(admin.ModelAdmin):
    list_display = ['i_profile', 'home_address']

@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ['school_name', 'is_active']

@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display  = ['class_name', 'is_active']

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ['route_name', 'is_active']

@admin.register(GuardianKids)
class GuardianKidsAdmin(admin.ModelAdmin):
    list_display = ['i_guardian_profile', 'i_school', 'i_class', 'i_route', 'kid_image', 'kid_name', 'id_card_number']

@admin.register(KidsIdCard)
class KidsIdCardAdmin(admin.ModelAdmin):
    list_display = ['i_kids', 'card_media']

@admin.register(DriverDetails)
class DriverDetailAdmin(admin.ModelAdmin):
    pass

@admin.register(Complaints)
class ComplaintsAdmin(admin.ModelAdmin):
    pass

@admin.register(DriverAttendance)
class DriverAttendanceAdmin(admin.ModelAdmin):
    pass