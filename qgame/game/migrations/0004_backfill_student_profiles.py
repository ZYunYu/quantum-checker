from django.db import migrations


def backfill_profiles(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Profile = apps.get_model('game', 'UserProfile')
    database = schema_editor.connection.alias
    for user_id in User.objects.using(database).values_list('id', flat=True).iterator():
        Profile.objects.using(database).get_or_create(user_id=user_id)


class Migration(migrations.Migration):
    dependencies = [('game', '0003_classroom_userprofile')]
    operations = [migrations.RunPython(backfill_profiles, migrations.RunPython.noop)]
