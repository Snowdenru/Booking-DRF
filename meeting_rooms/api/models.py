from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class Room(models.Model):
    name = models.CharField(max_length=100, unique=True)
    capacity = models.PositiveIntegerField()
    floor = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name} (floor {self.floor}, capacity {self.capacity})"


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="bookings")
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date", "start_time"]
        constraints = [
            models.UniqueConstraint(
                fields=["room", "date", "start_time"], name="unique_booking"
            )
        ]

    def __str__(self):
        return f"{self.user.email} booked {self.room.name} on {self.date} from {self.start_time} to {self.end_time}"

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError("End time must be after start time")

        # Check for overlapping bookings
        overlapping_bookings = Booking.objects.filter(
            room=self.room,
            date=self.date,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
        ).exclude(pk=self.pk if self.pk else None)

        if overlapping_bookings.exists():
            raise ValidationError(
                "This room is already booked for the selected time slot"
            )

        # Check if user has another booking at the same time
        user_overlapping_bookings = Booking.objects.filter(
            user=self.user,
            date=self.date,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
        ).exclude(pk=self.pk if self.pk else None)

        if user_overlapping_bookings.exists():
            raise ValidationError(
                "You already have a booking for the selected time slot"
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
