# Generated by Django 2.2.2 on 2019-08-05 08:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scouts', '0027_auto_20190802_1409'),
    ]

    operations = [
        migrations.AddField(
            model_name='scouttask',
            name='onboarding_property_details_id',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
