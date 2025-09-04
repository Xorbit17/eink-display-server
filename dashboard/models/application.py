from django.db import models
from dashboard.jobs.image_processing_declaration import (
    ART_STYLE_CHOICES, 
    QUALITY_CLASSIFICATION_CHOICES,
    CONTENT_TYPE_CLASSIFICATION_CHOICES,
    
)


class MinuteSystemSample(models.Model):
    minute = models.DateTimeField(unique=True, db_index=True)
    cpu_percent_avg = models.FloatField()
    mem_total = models.BigIntegerField()
    mem_used_avg = models.BigIntegerField()
    mem_available_avg = models.BigIntegerField()
    swap_total = models.BigIntegerField(null=True)
    swap_used_avg = models.BigIntegerField(null=True)
    rx_bps_avg = models.FloatField(null=True)
    tx_bps_avg = models.FloatField(null=True)

    class Meta:
        ordering = ["-minute"]

class PrerenderedDashboard(models.Model):
    path = models.TextField(null=True, default=None) # Null means dashboard was created but generation has crashed

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
