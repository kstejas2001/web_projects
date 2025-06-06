# Generated by Django 4.2 on 2025-05-28 10:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document_app', '0008_documentrequest_birth_time_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentrequest',
            name='death_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='documentrequest',
            name='death_time',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='documentrequest',
            name='deceased_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='documentrequest',
            name='place_of_death',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='documentrequest',
            name='relation_to_deceased',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
