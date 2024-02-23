# Generated by Django 4.2 on 2024-02-23 15:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0008_alter_complaints_status_driverattendance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='driverattendance',
            name='current_date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='driverdetails',
            name='i_profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='d_profile', to='user_management.profile'),
        ),
    ]
