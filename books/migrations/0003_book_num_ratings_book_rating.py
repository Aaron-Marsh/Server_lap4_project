# Generated by Django 4.0.6 on 2022-07-16 14:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0002_book_isbn'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='num_ratings',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='book',
            name='rating',
            field=models.IntegerField(default=0),
        ),
    ]
