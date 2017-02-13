from rest_framework.authtoken.models import Token

from activities.models import Activity

from .tasks import welcome_mail, vet_verify_mail


def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
        if not kwargs.get('raw', False):  # No loaddata trigger
            if not instance.is_vet():
                welcome_mail(instance, 'OWNER_BREEDER')


def vet_signal(sender, instance=None, created=False, **kwargs):
    if created:
        if not kwargs.get('raw', False):  # No loaddata trigger
            if instance.veterinarian_type == '4':
                instance.verified = True
                instance.save()
                vet_verify_mail(instance, instance.veterinarian_type)

            welcome_mail(instance.user, 'VET_TECH_STUDENT')


def follows_changed(instance, action=None, pk_set=None, **kwargs):
    if action == 'post_add' and pk_set:
        Activity.objects.update_or_create(
            follows_id=pk_set.pop(),
            action=Activity.FOLLOW,
            user=instance,
            defaults={'active': True}
        )
    elif action == 'post_remove' and pk_set:
        Activity.objects.update_or_create(
            follows_id=pk_set.pop(),
            action=Activity.FOLLOW,
            user=instance,
            defaults={'active': False}
        )
