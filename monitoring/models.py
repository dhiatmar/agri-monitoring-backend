from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class FarmProfile(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="farms",
    )
    location = models.CharField(max_length=255)
    size = models.FloatField(help_text="Farm size in hectares (or chosen unit)")
    crop_type = models.CharField(max_length=100)
    
    class Meta:
        verbose_name = "Farm Profile"
        verbose_name_plural = "Farm Profiles"
        ordering = ["owner_id", "location"]   # Tri par fermier puis région

    def __str__(self):
        return f"{self.crop_type} farm at {self.location} (id={self.id})"


class FieldPlot(models.Model):
    farm = models.ForeignKey(
        FarmProfile,
        on_delete=models.CASCADE,
        related_name="plots",
    )
    crop_variety = models.CharField(max_length=100)
    
    class Meta:
        verbose_name = "Field Plot"
        verbose_name_plural = "Field Plots"
        ordering = ["farm_id", "id"]  # Tri par ferme puis numéro de parcelle
   
    def __str__(self):
        return f"Plot {self.id} - {self.crop_variety} (farm {self.farm_id})"

class SensorReading(models.Model):
    SENSOR_TYPE_CHOICES = [
        ("moisture", "Soil moisture"),
        ("temperature", "Air temperature"),
        ("humidity", "Humidity"),
    ]

    timestamp = models.DateTimeField()
    plot = models.ForeignKey(
        FieldPlot,
        on_delete=models.CASCADE,
        related_name="sensor_readings",
    )
    sensor_type = models.CharField(max_length=20, choices=SENSOR_TYPE_CHOICES)
    value = models.FloatField()
    source = models.CharField(
        max_length=50,
        default="simulator",
        help_text="Source of the data (e.g., simulator)",
    )

    class Meta:
        verbose_name = "Sensor Reading"
        verbose_name_plural = "Sensor Readings"
        ordering = ["-timestamp"]  # plus récent en premier

    def __str__(self):
        return f"{self.sensor_type}={self.value} on plot {self.plot_id} at {self.timestamp}"

class AnomalyEvent(models.Model):
    SEVERITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    ]

    timestamp = models.DateTimeField(auto_now_add=True)
    plot = models.ForeignKey(
        FieldPlot,
        on_delete=models.CASCADE,
        related_name="anomalies",
    )
    anomaly_type = models.CharField(max_length=100)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    model_confidence = models.FloatField(
        help_text="Confidence score from the ML model (0–1)"
    )

    class Meta:
        verbose_name = "Anomaly Event"
        verbose_name_plural = "Anomaly Events"
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.anomaly_type} ({self.severity}) on plot {self.plot_id} at {self.timestamp}"


class AgentRecommendation(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    anomaly_event = models.ForeignKey(
        AnomalyEvent,
        on_delete=models.CASCADE,
        related_name="recommendations",
    )
    recommended_action = models.CharField(max_length=255)
    explanation_text = models.TextField()
    confidence = models.FloatField(
        help_text="Confidence score of the agent (0–1)"
    )

    class Meta:
        verbose_name = "Agent Recommendation"
        verbose_name_plural = "Agent Recommendations"
        ordering = ["-timestamp"]

    def __str__(self):
        return f"Recommendation {self.id} for anomaly {self.anomaly_event_id}"