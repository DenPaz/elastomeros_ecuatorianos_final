from allauth.account.models import EmailAddress
from django.core.management.base import BaseCommand

from apps.users.models import User

data = [
    {
        "first_name": "Dennis",
        "last_name": "Paz",
        "email": "dppazlopez@gmail.com",
        "is_staff": True,
        "is_superuser": True,
    },
    {
        "first_name": "Djalma",
        "last_name": "Paz",
        "email": "djalmapaz@gmail.com",
        "is_staff": True,
        "is_superuser": True,
    },
    {
        "first_name": "Narcisa",
        "last_name": "Lopez",
        "email": "elastomeros.ec@gmail.com",
        "is_staff": True,
        "is_superuser": True,
    },
]
password = "12345"  # noqa: S105


class Command(BaseCommand):
    help = "Create or update test users in the database."

    def handle(self, *args, **kwargs):
        for entry in data:
            lookup = {"email": entry["email"]}
            defaults = {k: v for k, v in entry.items() if k not in lookup}
            obj, created = User.objects.update_or_create(
                defaults=defaults,
                **lookup,
            )
            obj.set_password(password)
            obj.save()
            EmailAddress.objects.update_or_create(
                user=obj,
                email=obj.email,
                verified=True,
                primary=True,
            )
            action = "Created" if created else "Updated"
            style = self.style.SUCCESS if created else self.style.WARNING
            self.stdout.write(style(f"{action} user: {obj}"))
