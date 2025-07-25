# Generated by Django 5.2.3 on 2025-07-16 06:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='subscription',
            unique_together=set(),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='name',
            field=models.CharField(help_text='Subscription name (e.g., Netflix, Spotify)', max_length=255),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='next_payment_date',
            field=models.DateField(help_text='Next payment date'),
        ),
        migrations.RemoveField(
            model_name='subscription',
            name='auto_add_expense',
        ),
        migrations.RemoveField(
            model_name='subscription',
            name='category',
        ),
        migrations.RemoveField(
            model_name='subscription',
            name='description',
        ),
        migrations.RemoveField(
            model_name='subscription',
            name='end_date',
        ),
        migrations.RemoveField(
            model_name='subscription',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='subscription',
            name='start_date',
        ),
        migrations.RemoveField(
            model_name='subscription',
            name='website_url',
        ),
    ]
