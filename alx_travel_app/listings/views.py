from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils import timezone
from .models import Listing, Booking, Review, Payment
from .serializers import (
    ListingSerializer, ListingCreateSerializer,
    BookingSerializer, BookingCreateSerializer, 
    ReviewSerializer, ReviewCreateSerializer,
    PaymentSerializer, PaymentCreateSerializer,
    UserSerializer
)
from django.contrib.auth.models import User


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get current user profile",
        responses={200: UserSerializer}
    )
    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class ListingViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['location', 'price_per_night', 'is_available']
    search_fields = ['title', 'description', 'location', 'amenities']
    ordering_fields = ['price_per_night', 'created_at']
    ordering = ['-created_at']
    queryset = Listing.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return ListingCreateSerializer
        return ListingSerializer

    def perform_create(self, serializer):
        serializer.save(host=self.request.user)

    @swagger_auto_schema(
        operation_description="Create a new listing",
        request_body=ListingCreateSerializer,
        responses={
            201: ListingSerializer,
            400: "Bad Request"
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Get all listings with filtering and search",
        manual_parameters=[
            openapi.Parameter('location', openapi.IN_QUERY, description="Filter by location", type=openapi.TYPE_STRING),
            openapi.Parameter('search', openapi.IN_QUERY, description="Search in title, description, location, amenities", type=openapi.TYPE_STRING),
        ],
        responses={200: ListingSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Get listing details",
        responses={200: ListingSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class BookingViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['created_at', 'check_in_date']
    ordering = ['-created_at']

    def get_queryset(self):
        # Handle Swagger schema generation (user is anonymous)
        if getattr(self, 'swagger_fake_view', False):
            return Booking.objects.none()
        
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Booking.objects.all()
        return Booking.objects.filter(guest=user)

    def get_serializer_class(self):
        if self.action == 'create':
            return BookingCreateSerializer
        return BookingSerializer

    def perform_create(self, serializer):
        serializer.save(guest=self.request.user)

    @swagger_auto_schema(
        operation_description="Create a new booking",
        request_body=BookingCreateSerializer,
        responses={
            201: BookingSerializer,
            400: "Validation error"
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    @swagger_auto_schema(
        operation_description="Cancel a booking",
        responses={
            200: BookingSerializer,
            400: "Cannot cancel completed or already cancelled booking"
        }
    )
    def cancel(self, request, pk=None):
        booking = self.get_object()
        if booking.status == Booking.STATUS_COMPLETED:
            return Response(
                {"error": "Cannot cancel a completed booking."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if booking.status == Booking.STATUS_CANCELLED:
            return Response(
                {"error": "Booking is already cancelled."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.status = Booking.STATUS_CANCELLED
        booking.save()
        serializer = self.get_serializer(booking)
        return Response(serializer.data)


class ReviewViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['listing', 'rating']
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']
    queryset = Review.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return ReviewCreateSerializer
        return ReviewSerializer

    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)

    @swagger_auto_schema(
        operation_description="Create a new review",
        request_body=ReviewCreateSerializer,
        responses={
            201: ReviewSerializer,
            400: "Validation error - user can only review completed bookings"
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class PaymentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'payment_method']
    ordering_fields = ['created_at', 'amount']
    ordering = ['-created_at']

    def get_queryset(self):
        # Handle Swagger schema generation (user is anonymous)
        if getattr(self, 'swagger_fake_view', False):
            return Payment.objects.none()
        
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Payment.objects.all()
        return Payment.objects.filter(booking__guest=user)

    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentCreateSerializer
        return PaymentSerializer

    @swagger_auto_schema(
        operation_description="Create a new payment",
        request_body=PaymentCreateSerializer,
        responses={
            201: PaymentSerializer,
            400: "Validation error"
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    @swagger_auto_schema(
        operation_description="Simulate payment completion",
        responses={200: PaymentSerializer}
    )
    def complete(self, request, pk=None):
        payment = self.get_object()
        # Create a simple transaction ID for demo
        import uuid
        payment.mark_as_completed(transaction_id=f"txn_{uuid.uuid4().hex[:16]}")
        serializer = self.get_serializer(payment)
        return Response(serializer.data)


# Statistics View
from rest_framework.views import APIView
from django.db.models import Count, Avg, Sum

class StatsAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Get travel app statistics",
        responses={
            200: openapi.Response(
                description="Statistics data",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'total_listings': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'total_bookings': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'total_revenue': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'average_rating': openapi.Schema(type=openapi.TYPE_NUMBER),
                    }
                )
            )
        }
    )
    def get(self, request):
        stats = {
            'total_listings': Listing.objects.count(),
            'total_bookings': Booking.objects.count(),
            'total_revenue': Payment.objects.filter(status='completed').aggregate(
                total=Sum('amount')
            )['total'] or 0,
            'average_rating': Review.objects.aggregate(
                avg_rating=Avg('rating')
            )['avg_rating'] or 0,
        }
        return Response(stats)