from django.urls import path
from .views import (
    FarmProfileListView,
    FieldPlotListView,
    SensorReadingView,
    AnomalyEventListView,
    AgentRecommendationListView,
)

urlpatterns = [
    path("farms/", FarmProfileListView.as_view(), name="farm-list"),
    path("plots/", FieldPlotListView.as_view(), name="plot-list"),
    path("sensor-readings/", SensorReadingView.as_view(), name="sensor-readings"),
    path("anomalies/", AnomalyEventListView.as_view(), name="anomaly-list"),
    path("recommendations/", AgentRecommendationListView.as_view(), name="recommendation-list"),
]
