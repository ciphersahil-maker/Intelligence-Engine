from django.db import models

# Create your models here.

class Record(models.Model):
    user_id = models.IntegerField()
    value = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['created_at'])
        ]


from django.db import models


class Booking(models.Model):

    client_name                 = models.CharField(max_length=255)
    team_member_name            = models.CharField(max_length=255)

    team_member_status          = models.CharField(max_length=100)

    country                     = models.CharField(max_length=100, blank=True, null=True)
    city                        = models.CharField(max_length=100)

    locations                   = models.JSONField(default=list, blank=True, null=True)   # NEW

    job_status                  = models.CharField(max_length=100)

    booked_date                 = models.DateField()
    booked_end_date             = models.DateField()

    booked_start_time           = models.TimeField()
    booked_end_time             = models.TimeField()

    client_hourly_rate          = models.FloatField()

    credit_card_fee             = models.FloatField(default=0)
    rush_fee                    = models.FloatField(default=0)
    gratuity                    = models.FloatField(default=0)

    total_client_charge         = models.FloatField(null=True, blank=True)

    number_of_children          = models.IntegerField()

    category                    = models.CharField(max_length=100)

    notes                       = models.TextField(blank=True, null=True)

    client_confirm_notes        = models.TextField(null=True, blank=True)

    ages_of_children            = models.CharField(max_length=255, blank=True, null=True)  # NEW

    pet_selection               = models.JSONField(default=list)

    deposit_amount              = models.FloatField(null=True, blank=True)

    booking_fee                 = models.FloatField(default=0)

    nanny_trial                 = models.CharField(max_length=50, blank=True, null=True)

    created_at                  = models.DateTimeField(auto_now_add=True)



    def __str__(self):
        return f"{self.client_name} --- {self.team_member_name}"
    
    class Meta:
        db_table = "booking"
        indexes = [
            models.Index(fields=['city']),
        ]