# Generated by Django 4.1.5 on 2023-03-12 12:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('climate', '0011_colour_alter_item_item_cost_alter_wearing_creature_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='creature',
            name='colour',
        ),
        migrations.AddField(
            model_name='creature',
            name='eye_colour',
            field=models.ForeignKey(default='blue', on_delete=django.db.models.deletion.SET_DEFAULT, related_name='eye_colour', to='climate.colour'),
        ),
        migrations.AddField(
            model_name='creature',
            name='fur_colour',
            field=models.ForeignKey(default='black', on_delete=django.db.models.deletion.SET_DEFAULT, related_name='fur_colour', to='climate.colour'),
        ),
    ]