from django.core.management.base import BaseCommand
from wagtail.images.models import Rendition


class Command(BaseCommand):
    help = "Delete Rendition objects that are PNG or JPEG files"

    def handle(self, *args, **options):
        # Find all renditions with PNG or JPEG files
        all_renditions = [
            rendition
            for rendition in Rendition.objects.all()
            if rendition.file
            and rendition.file.name
            and rendition.file.name.lower().endswith((".png", ".jpg", ".jpeg"))
        ]

        total_count = len(all_renditions)

        if total_count == 0:
            self.stdout.write(
                self.style.SUCCESS(
                    "No PNG or JPEG renditions found. Nothing to delete."
                )
            )
            return

        # Limit to 25 renditions at a time
        renditions_to_delete = all_renditions[:25]

        # Delete the renditions
        deleted_count = 0
        for rendition in renditions_to_delete:
            try:
                rendition.delete()
                deleted_count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"Error deleting rendition {rendition.id}: {str(e)}"
                    )
                )

        remaining = total_count - 25 if total_count > 25 else 0
        if remaining > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Deleted {deleted_count} PNG/JPEG rendition(s). "
                    f"{remaining} remaining. Run again to delete more."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Deleted {deleted_count} out of {total_count} PNG/JPEG rendition(s)."
                )
            )
