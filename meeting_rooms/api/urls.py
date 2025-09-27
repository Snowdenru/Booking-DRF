from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RoomViewSet, BookingViewSet, UserRegistrationViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r'rooms', RoomViewSet, basename='rooms')
router.register(r'bookings', BookingViewSet, basename='bookings')
router.register(r'auth', UserRegistrationViewSet, basename='auth')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]