# Generated by Django 2.2.4 on 2019-09-03 23:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='avatar',
            field=models.ImageField(blank=True, upload_to='avatar/%Y%m%d/'),
        ),
    ]
