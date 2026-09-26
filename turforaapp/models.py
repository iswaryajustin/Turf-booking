from django.db import models

class Playerdetail(models.Model):
     username=models.CharField(max_length=10)
     email=models.EmailField(unique=True)
     phone=models.CharField(max_length=10)
     password=models.CharField(max_length=10)
     confirmPassword=models.CharField(max_length=10)
     is_block = models.BooleanField(default=False)


class Turf(models.Model):
    turf_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    turf_type = models.CharField(max_length=50)
    image = models.ImageField(upload_to='turf_images/', blank=True, null=True)
    description = models.TextField()
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
    available_facilities = models.TextField()
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    address = models.CharField(max_length=255)
    opening_time = models.TimeField()
    closing_time = models.TimeField()

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.turf_name



class Booking(models.Model):
    turf = models.ForeignKey(Turf, on_delete=models.CASCADE)
    player = models.ForeignKey(Playerdetail, on_delete=models.CASCADE)

    booking_date = models.DateField()

    start_time = models.TimeField()
    end_time = models.TimeField()

    price = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(
        max_length=20,
        choices=[
            ('confirmed', 'Confirmed'),
            ('cancelled', 'Cancelled'),
        ],
        default='confirmed'
    )


    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.turf.turf_name} - {self.booking_date} - {self.start_time}"



class Payment(models.Model):

    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_date = models.DateTimeField(
        auto_now_add=True
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ('paid', 'Paid'),
            ('pending', 'Pending'),
            ('failed', 'Failed'),
            ('refunded', 'Refunded'),
        ],
        default='pending'
    )

    def __str__(self):
        return f"Payment - TUR-{self.booking.id}"



class Review(models.Model):
    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name='review'
    )

    player = models.ForeignKey(
        Playerdetail,
        on_delete=models.CASCADE
    )

    turf = models.ForeignKey(
        Turf,
        on_delete=models.CASCADE
    )

    rating = models.IntegerField(
        choices=[
            (1, '1'),
            (2, '2'),
            (3, '3'),
            (4, '4'),
            (5, '5'),
        ]
    )

    review = models.TextField()
    is_flagged = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.player.username} - {self.turf.turf_name}"


class TurfSlot(models.Model):
    turf = models.ForeignKey(Turf, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.start_time} - {self.end_time}"


class BlockedSlot(models.Model):
    turf = models.ForeignKey(Turf, on_delete=models.CASCADE)
    date = models.DateField()
    from_time = models.TimeField()
    to_time = models.TimeField()
    reason = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.turf.turf_name} - {self.date}"


class TurfHoliday(models.Model):
    STATUS_CHOICES = [
        ('maintenance', 'Maintenance'),
        ('holiday', 'Holiday'),
        ('inactive', 'Inactive'),
    ]

    turf = models.ForeignKey(Turf, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    reason = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.turf.turf_name} - {self.status}"


class Notification(models.Model):

    NOTIFICATION_TYPES = [
        ('confirmation', 'Booking Confirmation'),
        ('cancellation', 'Booking Cancellation'),
        ('reminder', 'Booking Reminder'),
        ('status_change', 'Booking Status Change'),
    ]

    player = models.ForeignKey(
        Playerdetail,
        on_delete=models.CASCADE
    )

    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    notification_type = models.CharField(
        max_length=30,
        choices=NOTIFICATION_TYPES
    )

    message = models.TextField()

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.player.username} - {self.notification_type}"