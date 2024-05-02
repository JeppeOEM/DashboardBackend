# Generated by Django 3.2.25 on 2024-04-29 19:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20240429_1713'),
    ]

    operations = [
        migrations.CreateModel(
            name='Coin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.RemoveField(
            model_name='strategy',
            name='link',
        ),
        migrations.RemoveField(
            model_name='strategy',
            name='price',
        ),
        migrations.RemoveField(
            model_name='strategy',
            name='time_minutes',
        ),
        migrations.RemoveField(
            model_name='strategy',
            name='title',
        ),
        migrations.AddField(
            model_name='strategy',
            name='base',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='base_strategies', to='core.coin'),
        ),
        migrations.AddField(
            model_name='strategy',
            name='coins',
            field=models.ManyToManyField(to='core.Coin'),
        ),
    ]
