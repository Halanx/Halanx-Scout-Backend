# Generated by Django 2.2.2 on 2019-06-15 05:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scouts', '0011_auto_20190613_1342'),
    ]

    operations = [
        migrations.AddField(
            model_name='scout',
            name='gcm_id',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
