"""Management command to seed initial website data."""
import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.db import transaction


class Command(BaseCommand):
    help = "Seed the database with initial website data (skills, experience, projects, site settings)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--noinput",
            action="store_true",
            help="Do not prompt for confirmation",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        noinput = options["noinput"]

        if not noinput:
            self.stdout.write(
                self.style.WARNING(
                    "This will seed the database with initial data. "
                    "Existing data may be duplicated or overwritten."
                )
            )
            confirm = input("Do you want to continue? [y/N]: ")
            if confirm.lower() != "y":
                self.stdout.write("Seeding cancelled.")
                return

        fixtures_dir = Path(__file__).resolve(
        ).parent.parent.parent / "fixtures"

        # Load fixtures in order
        fixtures = [
            ("initial_skills.json", "Skills"),
            ("initial_experience.json", "Experience"),
            ("initial_projects.json", "Projects"),
        ]

        self.stdout.write("\nSeeding initial data...\n")

        for fixture_file, label in fixtures:
            fixture_path = fixtures_dir / fixture_file
            if not fixture_path.exists():
                raise CommandError(f"Fixture file not found: {fixture_path}")

            try:
                with open(fixture_path) as f:
                    data = json.load(f)
                    count = len(data)
                call_command("loaddata", str(fixture_path), verbosity=0)
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Loaded {count} {label}")
                )
            except Exception as e:
                raise CommandError(f"Error loading {label}: {e}")

        # Create SiteSettings if not exists
        self._seed_site_settings()

        self.stdout.write(
            self.style.SUCCESS(
                "\n✓ Database seeded successfully!\n"
            )
        )

    def _seed_site_settings(self):
        """Create default SiteSettings if it doesn't exist."""
        from core.models import SiteSettings

        if SiteSettings.objects.exists():
            self.stdout.write(
                self.style.WARNING("⚠ SiteSettings already exists (skipping)")
            )
            return

        site_settings = SiteSettings(
            site_title="GEORGE OGOLA // Architect",
            site_tagline="Building scalable systems that don't break at 3 AM.",
            email="gogola89@gmail.com",
            location="Nairobi, Kenya",
        )
        site_settings.save()
        self.stdout.write(self.style.SUCCESS("✓ Created SiteSettings"))
