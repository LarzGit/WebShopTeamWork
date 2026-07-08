from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def create_default_groups(sender, **kwargs):
    if sender.name != 'accounts':
        return

    Group.objects.get_or_create(name='Customer')
    admin_group, _ = Group.objects.get_or_create(name='Administrator')
    admin_group.permissions.set(Permission.objects.all())