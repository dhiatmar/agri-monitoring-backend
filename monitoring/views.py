from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated

from .models import (
    FarmProfile,
    FieldPlot,
    SensorReading,
    AnomalyEvent,
    AgentRecommendation,
)

from .serializers import (
    FarmProfileSerializer,
    FieldPlotSerializer,
    SensorReadingSerializer,
    AnomalyEventSerializer,
    AgentRecommendationSerializer,
)


# -------------------- Farms & Plots -------------------- #

class FarmProfileListView(generics.ListAPIView):
    """
    GET /api/farms/
    Retourne la liste des fermes.
    """
    queryset = FarmProfile.objects.all()
    serializer_class = FarmProfileSerializer


class FieldPlotListView(generics.ListAPIView):
    """
    GET /api/plots/
    Optionnel : /api/plots/?farm=<id> pour filtrer par ferme.
    """
    serializer_class = FieldPlotSerializer

    def get_queryset(self):
        qs = FieldPlot.objects.all()
        farm_id = self.request.query_params.get("farm")
        if farm_id is not None:
            qs = qs.filter(farm_id=farm_id)
        return qs


# -------------------- Sensor Readings -------------------- #

class SensorReadingView(APIView):
    """
    GET /api/sensor-readings/?plot=<id>  -> liste des mesures (optionnellement filtrées par parcelle)
    POST /api/sensor-readings/           -> ingestion d'une nouvelle mesure
    """
    permission_classes = [IsAuthenticated]
    def get(self, request):
        plot_id = request.query_params.get("plot")
        queryset = SensorReading.objects.all().order_by("-timestamp")

        if plot_id is not None:
            queryset = queryset.filter(plot_id=plot_id)

        serializer = SensorReadingSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = SensorReadingSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # 1) Sauvegarde de la mesure
        reading = serializer.save()

        # 2) TODO: appeler ici le module ML + Agent plus tard
        #    Exemple plus tard:
        #    anomaly_data = detect_anomaly_for_reading(reading)
        #    if anomaly_data:
        #        anomaly = AnomalyEvent.objects.create(...)
        #        generate_recommendation(anomaly)

        return Response(
            SensorReadingSerializer(reading).data,
            status=status.HTTP_201_CREATED,
        )


# -------------------- Anomalies & Recommendations -------------------- #

class AnomalyEventListView(generics.ListAPIView):
    """
    GET /api/anomalies/
    Optionnel : /api/anomalies/?plot=<id> pour filtrer par parcelle.
    """
    serializer_class = AnomalyEventSerializer

    def get_queryset(self):
        qs = AnomalyEvent.objects.all().order_by("-timestamp")
        plot_id = self.request.query_params.get("plot")
        if plot_id is not None:
            qs = qs.filter(plot_id=plot_id)
        return qs


class AgentRecommendationListView(generics.ListAPIView):
    """
    GET /api/recommendations/
    Optionnel :
      - /api/recommendations/?plot=<id>
      - /api/recommendations/?anomaly=<id>
    """
    serializer_class = AgentRecommendationSerializer

    def get_queryset(self):
        qs = AgentRecommendation.objects.all().order_by("-timestamp")

        anomaly_id = self.request.query_params.get("anomaly")
        plot_id = self.request.query_params.get("plot")

        if anomaly_id is not None:
            qs = qs.filter(anomaly_event_id=anomaly_id)

        if plot_id is not None:
            qs = qs.filter(anomaly_event__plot_id=plot_id)

        return qs
