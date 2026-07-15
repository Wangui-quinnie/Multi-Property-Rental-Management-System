import uuid

from django.db import models
from django.utils import timezone


class TimeStampedUUIDModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ArchivableQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_archived=False)

    def archived(self):
        return self.filter(is_archived=True)

    def archive(self):
        return self.update(is_archived=True, archived_at=timezone.now())

    def restore(self):
        return self.update(is_archived=False, archived_at=None)


class ArchivableManager(models.Manager):
    def get_queryset(self):
        # Default manager (Model.objects) excludes archived rows.
        return ArchivableQuerySet(self.model, using=self._db).active()

    def with_archived(self):
        return ArchivableQuerySet(self.model, using=self._db)


class AllObjectsManager(models.Manager):
    def get_queryset(self):
        # Unfiltered — includes archived rows — but still returns an
        # ArchivableQuerySet, so .archive()/.restore() work here too.
        return ArchivableQuerySet(self.model, using=self._db)


class ArchivableModel(models.Model):
    is_archived = models.BooleanField(default=False, db_index=True)
    archived_at = models.DateTimeField(null=True, blank=True)

    objects = ArchivableManager()
    all_objects = AllObjectsManager()

    class Meta:
        abstract = True

    def archive(self):
        self.is_archived = True
        self.archived_at = timezone.now()
        self.save(update_fields=["is_archived", "archived_at"])

    def restore(self):
        self.is_archived = False
        self.archived_at = None
        self.save(update_fields=["is_archived", "archived_at"])