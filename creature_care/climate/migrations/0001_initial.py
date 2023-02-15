# Generated by Django 4.1.5 on 2023-02-15 17:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Advice',
            fields=[
                ('advice_id', models.IntegerField(primary_key=True, serialize=False, unique=True)),
                ('content', models.CharField(max_length=500)),
                ('source', models.CharField(max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name='Creature',
            fields=[
                ('creature_id', models.IntegerField(auto_created=True, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(default='Creature', max_length=50)),
                ('colour', models.CharField(default='black', max_length=16)),
                ('thirst', models.IntegerField(default=0)),
                ('litter', models.IntegerField(default=0)),
                ('last_thirst_refill', models.DateTimeField()),
                ('food', models.IntegerField(default=0)),
                ('last_food_refill', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('item_id', models.IntegerField(primary_key=True, serialize=False, unique=True)),
                ('item_name', models.CharField(max_length=40)),
                ('item_cost', models.IntegerField()),
                ('item_img', models.FileField(upload_to='')),
                ('item_class', models.CharField(max_length=25)),
            ],
        ),
        migrations.CreateModel(
            name='Wearing',
            fields=[
                ('wearing_id', models.IntegerField(primary_key=True, serialize=False, unique=True)),
                ('creature_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='climate.creature')),
                ('item_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='climate.item')),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('profile_id', models.IntegerField(primary_key=True, serialize=False, unique=True)),
                ('points', models.IntegerField(default=0)),
                ('access_level', models.IntegerField(default=1)),
                ('num_times_watered', models.IntegerField(default=0)),
                ('num_times_fed', models.IntegerField(default=0)),
                ('num_times_litter_cleared', models.IntegerField(default=0)),
                ('creature_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='climate.creature')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
