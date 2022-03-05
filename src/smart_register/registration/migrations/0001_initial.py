import django.contrib.postgres.fields.citext
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataSet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', django.contrib.postgres.fields.citext.CICharField(max_length=255, unique=True)),
                ('start', models.DateField(auto_now_add=True)),
                ('end', models.DateField(blank=True, null=True)),
                ('flex_form', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.flexform')),
            ],
        ),
        migrations.CreateModel(
            name='Record',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateField(auto_now_add=True)),
                ('data', models.JSONField(default=dict)),
                ('registration', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='registration.dataset')),
            ],
        ),
    ]
