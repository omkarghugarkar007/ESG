# Generated by Django 4.2.11 on 2024-03-14 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apidocument',
            name='api_document',
            field=models.FileField(upload_to='api_docs/'),
        ),
    ]
