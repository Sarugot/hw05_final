# Generated by Django 2.2.19 on 2022-10-21 17:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_auto_20221021_2126'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='slug',
            field=models.SlugField(max_length=255, unique=True),
        ),
    ]
