# Generated by Django 3.0.8 on 2020-08-12 17:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0008_auto_20200812_1830'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bid',
            old_name='user',
            new_name='owner',
        ),
    ]
