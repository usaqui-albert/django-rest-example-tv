from rest_framework.authtoken.models import Token

from activities.models import Activity

from .tasks import welcome_mail, vet_verify_mail


def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
        if not instance.is_vet():
            welcome_mail.delay(instance, 'OWNER_BREEDER')


def vet_signal(sender, instance=None, created=False, **kwargs):
    if created:
        if instance.veterinarian_type == '4':
            instance.verified = True
            instance.save()
            vet_verify_mail.delay(instance, instance.veterinarian_type)

        welcome_mail.delay(instance, 'VET_TECH_STUDENT')


def follows_changed(sender, action=None, pk_set=None, **kwargs):
    if action == 'post_add':
        activity = Activity(
            follows_id=pk_set.pop(),
            action=Activity.FOLLOW,
            user=kwargs['instance']
        )
        activity.save()
