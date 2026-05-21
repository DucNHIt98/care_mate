from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_post_author'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.DeleteModel(name='Post'),
            ],
        ),
    ]
