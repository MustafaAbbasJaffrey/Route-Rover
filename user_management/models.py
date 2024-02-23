import random
from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField
from datetime import datetime ,date
from django.conf import settings
import os
from django.utils import timezone
from ckeditor.fields import RichTextField

# Create your models here.

def save_profile_image(instance, filename):
    file_extension = os.path.splitext(filename)[1].lstrip('.')
    current_datetime = datetime.now().strftime('%Y%m%d%H%M%S')
    target_dir = f'profile_images/{instance.user.pk}'
    file_dir = os.path.join(settings.MEDIA_ROOT, target_dir)
    if not os.path.isdir(file_dir):
        os.makedirs(file_dir, 0o777)
    return os.path.join(target_dir, f'{current_datetime}.{file_extension}')

def save_kid_image(instance, filename):
    file_extension = os.path.splitext(filename)[1].lstrip('.')
    current_datetime = datetime.now().strftime('%Y%m%d%H%M%S')
    target_dir = f'kid_images/{instance.i_guardian_profile.pk}'
    file_dir = os.path.join(settings.MEDIA_ROOT, target_dir)
    if not os.path.isdir(file_dir):
        os.makedirs(file_dir, 0o777)
    return os.path.join(target_dir, f'{current_datetime}.{file_extension}')

def save_kids_card(instance, filename):
    file_extension = os.path.splitext(filename)[1].lstrip('.')
    current_datetime = datetime.now().strftime('%Y%m%d%H%M%S')
    target_dir = f'kids_idcard/{instance.i_kids.pk}'
    file_dir = os.path.join(settings.MEDIA_ROOT, target_dir)
    if not os.path.isdir(file_dir):
        os.makedirs(file_dir, 0o777)
    return os.path.join(target_dir, f'{current_datetime}.{file_extension}')


class Role(models.Model):
    name = models.CharField(max_length=50)
    display_name = models.CharField(max_length=50, default="")
    created_on = models.DateTimeField(auto_now_add=True)
    active=models.BooleanField(default=False)

    @classmethod
    def get_default_role(cls):
        obj, _ = cls.objects.get_or_create(
            name="driver",
            defaults={
                    "name": "driver",
                    "display_name": "Driver",
                    "active": True
            }
        )
        return obj.pk

    def __str__(self):
        return self.name

class Profile(models.Model):

    # user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name = "profile_user")
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name = "profile")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="user_role", default=Role.get_default_role)
    join_date = models.DateField(default=date.today)
    phone_number = PhoneNumberField(null=True, blank=True)
    main_image = models.FileField(max_length=256, upload_to = save_profile_image, null=True, blank=True)
    is_delete = models.BooleanField(default=False)
    notification = models.BooleanField(default=True)
    state = models.CharField(blank=True , null = True)
    country = models.CharField(blank=True , null = True)
    city = models.CharField(blank=True , null = True)
    # date_of_birth = models.DateField(null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return '%s' % self.user.email
    
    def get_main_image(self):
        profile_photo_path = None
        try:
            profile_photo_index = self.main_image.path.split("/").index('media')
            profile_photo_path =  "/"+"/".join(self.main_image.path.split("/")[profile_photo_index:])
        except Exception: pass
        return profile_photo_path
    
    def get_full_name(self):
        return self.user.first_name+" "+self.user.last_name
    
    def user_role(self):
        return self.role.name
        
    class Meta:
        db_table = 'profile'

class GuardianDetails(models.Model):
    i_profile = models.ForeignKey(Profile, on_delete = models.CASCADE)
    home_address = models.CharField(max_length = 512)

    def __str__(self):
        return '%s' % self.i_profile.user.email
    
    class Meta:
        db_table = 'guardian_details'
    
class School(models.Model):
    school_name = models.CharField(max_length = 256)
    is_active = models.BooleanField(default = True)

    def __str__(self):
        return '%s' % self.school_name
    class Meta:
        db_table = 'school'

class SchoolClass(models.Model):
    class_name = models.CharField(max_length = 256)
    is_active = models.BooleanField(default = True)

    def __str__(self):
        return '%s' % self.class_name
    class Meta:
        db_table = 'school_class'

class Route(models.Model):
    route_name = models.CharField(max_length = 256)
    is_active = models.BooleanField(default = True)

    def __str__(self):
        return '%s' % self. route_name

    class Meta:
        db_table = 'route'

class GuardianKids(models.Model):
    i_guardian_profile = models.ForeignKey(GuardianDetails, on_delete = models.CASCADE)
    i_school = models.ForeignKey(School, on_delete = models.CASCADE)
    i_class = models.ForeignKey(SchoolClass, on_delete = models.CASCADE)
    i_route = models.ForeignKey(Route, on_delete = models.CASCADE)
    kid_image = models.FileField(max_length=256, upload_to = save_kid_image, null=True, blank=True)
    kid_name = models.CharField(max_length = 256)
    id_card_number = models.CharField(max_length = 100, null = True, blank = True)

    def __str__(self):
        return '%s' %  self.kid_name

    def get_kid_image(self):
        profile_photo_path = None
        try:
            profile_photo_index = self.kid_image.path.split("/").index('media')
            profile_photo_path =  "/"+"/".join(self.kid_image.path.split("/")[profile_photo_index:])
        except Exception: pass
        return profile_photo_path
    
    class Meta:
        db_table = 'guardian_kids'
    
class KidsIdCard(models.Model):
    i_kids = models.ForeignKey(GuardianKids, on_delete = models.CASCADE)
    card_media = models.FileField(max_length=256, upload_to = save_kids_card, null=True, blank=True)

    def __str__(self):
        return '%s' % self.i_kids.kid_name
    
    def get_card_media(self):
        main_path =  None
        try:
            main_index = self.card_media.path.split("/").index('media')
            main_path =  "/"+"/".join(self.card_media.path.split("/")[main_index:])
        except Exception: pass
        return main_path
    
    class Meta:
        db_table = 'kids_card'

class Language(models.Model):
    name = models.CharField(max_length=100)
    added_by = models.ForeignKey(
        "user_management.Profile",
        on_delete=models.CASCADE,
        related_name="language_admin",
        null=True,
        blank=True,
        default=""
    )
    added_on = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    class Meta:
        ordering = ['name']
        db_table = 'all_languages'

class GlobalConfiguration(models.Model):
    name = models.CharField(max_length=36)
    value = models.CharField(max_length=128)

    def __str__(self):
        return '%s' % self.name

    class Meta:
        db_table = 'global_configuration'
