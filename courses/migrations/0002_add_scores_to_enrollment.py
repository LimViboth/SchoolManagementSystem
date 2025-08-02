from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='enrollment',
            name='assignment_score',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='enrollment',
            name='midterm_score',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='enrollment',
            name='final_score',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
