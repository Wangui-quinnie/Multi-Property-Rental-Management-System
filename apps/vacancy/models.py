from django.db import models
from django.utils import timezone

from apps.core.models import TimeStampedUUIDModel
from apps.properties.models import Unit


class VacancyPeriod(TimeStampedUUIDModel):
    unit = models.ForeignKey(
        Unit,
        on_delete=models.PROTECT,
        related_name="vacancy_periods",
    )
    vacated_at = models.DateField()
    occupied_at = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "Vacancy Period"
        verbose_name_plural = "Vacancy Periods"
        ordering = ["-vacated_at"]
        indexes = [
            models.Index(fields=["unit", "occupied_at"]),
        ]

    @property
    def is_open(self):
        return self.occupied_at is None

    @property
    def days_vacant(self):
        end = self.occupied_at or timezone.localdate()
        return (end - self.vacated_at).days

    def __str__(self):
        status = "ongoing" if self.is_open else f"ended {self.occupied_at}"
        return f"{self.unit} vacant since {self.vacated_at} ({status})"