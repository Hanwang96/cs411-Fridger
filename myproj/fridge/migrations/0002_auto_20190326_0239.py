# Generated by Django 2.1.7 on 2019-03-26 02:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fridge', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe_ingredient',
            name='ingredient_type',
        ),
        migrations.AddField(
            model_name='ingredient',
            name='ingredient_type',
            field=models.CharField(default='general', max_length=200),
            preserve_default=False,
        ),
    ]
