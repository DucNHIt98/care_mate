from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def update_content_type(apps, schema_editor):
    ContentType = apps.get_model('contenttypes', 'ContentType')
    ContentType.objects.filter(app_label='core', model='post').update(app_label='post')


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_move_post_to_post_app'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='Post',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('title', models.CharField(max_length=255)),
                        ('content', models.TextField()),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='posts', to=settings.AUTH_USER_MODEL)),
                    ],
                    options={
                        'db_table': 'core_post',
                        'ordering': ['-created_at'],
                    },
                ),
            ],
        ),
        migrations.RunPython(update_content_type, migrations.RunPython.noop),
    ]
