from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Room, Booking
from .serializers import RoomSerializer, BookingSerializer, UserRegistrationSerializer
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth import get_user_model


from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

User = get_user_model()
class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['capacity', 'floor']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticatedOrReadOnly()]
    

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'date',
                openapi.IN_QUERY,
                description='Date for availability check (default: today)',
                type=openapi.TYPE_STRING,
                format='date',
                required=False
            ),
            openapi.Parameter(
                'start_time',
                openapi.IN_QUERY,
                description='Start time for availability check',
                type=openapi.TYPE_STRING,
                format='time',
                required=True
            ),
            openapi.Parameter(
                'end_time',
                openapi.IN_QUERY,
                description='End time for availability check',
                type=openapi.TYPE_STRING,
                format='time',
                required=True
            ),
            openapi.Parameter(
                'capacity',
                openapi.IN_QUERY,
                description='Minimum room capacity',
                type=openapi.TYPE_INTEGER,
                required=False
            ),
            openapi.Parameter(
                'floor',
                openapi.IN_QUERY,
                description='Floor number',
                type=openapi.TYPE_INTEGER,
                required=False
            ),
        ]
    )
    @action(detail=False, methods=['get'])
    def available(self, request):
        date = request.query_params.get('date', timezone.localdate())
        start_time = request.query_params.get('start_time')
        end_time = request.query_params.get('end_time')
        
        if not (start_time and end_time):
            return Response(
                {"detail": "Both start_time and end_time are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get rooms that are not booked for the requested time
        booked_rooms = Booking.objects.filter(
            date=date,
            start_time__lt=end_time,
            end_time__gt=start_time
        ).values_list('room_id', flat=True)
        
        queryset = self.get_queryset().exclude(id__in=booked_rooms)
        
        # Apply additional filters if provided
        capacity = request.query_params.get('capacity')
        if capacity:
            queryset = queryset.filter(capacity__gte=capacity)
        
        floor = request.query_params.get('floor')
        if floor:
            queryset = queryset.filter(floor=floor)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['room', 'date']
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Booking.objects.all()
        return Booking.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class UserRegistrationViewSet(viewsets.GenericViewSet):
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {"detail": "User registered successfully"},
            status=status.HTTP_201_CREATED
        )