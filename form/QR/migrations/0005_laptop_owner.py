# Generated by Django 3.0.2 on 2020-01-10 20:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('QR', '0004_auto_20200110_1716'),
    ]

    operations = [
        migrations.AddField(
            model_name='laptop',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='laptops', to='QR.Owner'),
        ),
    ]
