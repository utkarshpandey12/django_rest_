# Generated by Django 4.0.8 on 2023-02-07 01:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_mbxuser_refered_by_user_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='mbxuser',
            name='profession',
            field=models.CharField(blank=True, choices=[('Cattle', 'cattle_owners'), ('Trading', 'traders_desc'), ('Kirana', 'kirana_stores'), ('Other', 'other_categories')], max_length=10),
        ),
    ]
