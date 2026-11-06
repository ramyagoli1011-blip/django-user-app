from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.utils import timezone

from admin_panel.db import get_admins


class Command(BaseCommand):
    help = "Create the first Super Admin"

    def handle(self, *args, **kwargs):
        email = settings.SUPER_ADMIN_EMAIL
        password = settings.SUPER_ADMIN_PASSWORD

        if not email or not password:
            self.stdout.write(
                self.style.ERROR("Super Admin credentials missing in .env")
            )
            return

        admins = get_admins()
        email = email.strip().lower()

        admins.create_index("email", unique=True)

        old = admins.find_one({"email": email})

        if old:
            self.stdout.write(
                self.style.WARNING("Super Admin already exists.")
            )
            return

        admins.insert_one({
            "email": email,
            "password": make_password(password),
            "role": "super_admin",
            "active": True,
            "created_at": timezone.now()
        })

        self.stdout.write(
            self.style.SUCCESS("Super Admin created successfully!")
        )