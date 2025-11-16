import uuid
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Listing, Booking, Review, Payment
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class ListingSerializer(serializers.ModelSerializer):
    host = UserSerializer(read_only=True)
    host_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), 
        source='host', 
        write_only=True
    )
    amenities_list = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    total_reviews = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = [
            'listing_id', 'title', 'description', 'price_per_night', 
            'location', 'amenities', 'amenities_list', 'host', 'host_id',
            'is_available', 'created_at', 'updated_at', 'average_rating', 'total_reviews'
        ]
        read_only_fields = ['listing_id', 'created_at', 'updated_at', 'average_rating', 'total_reviews']

    def get_amenities_list(self, obj):
        return obj.get_amenities_list()

    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return 0

    def get_total_reviews(self, obj):
        return obj.reviews.count()

    def validate_price_per_night(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price per night must be greater than 0.")
        return value


class BookingSerializer(serializers.ModelSerializer):
    listing = ListingSerializer(read_only=True)
    listing_id = serializers.PrimaryKeyRelatedField(
        queryset=Listing.objects.all(), 
        source='listing', 
        write_only=True
    )
    guest = UserSerializer(read_only=True)
    guest_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), 
        source='guest', 
        write_only=True
    )
    duration = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()

    class Meta:
        model = Booking
        fields = [
            'booking_id', 'listing', 'listing_id', 'guest', 'guest_id',
            'check_in_date', 'check_out_date', 'total_price', 'status',
            'duration', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['booking_id', 'total_price', 'created_at', 'updated_at']

    def validate(self, data):
        """
        Validate booking dates and availability
        """
        check_in = data.get('check_in_date')
        check_out = data.get('check_out_date')
        listing = data.get('listing')

        if check_in and check_out:
            if check_in >= check_out:
                raise serializers.ValidationError({
                    "check_out_date": "Check-out date must be after check-in date."
                })

            from django.utils import timezone
            if check_in < timezone.now().date():
                raise serializers.ValidationError({
                    "check_in_date": "Check-in date cannot be in the past."
                })

            if listing:
                overlapping_bookings = Booking.objects.filter(
                    listing=listing,
                    status__in=[Booking.STATUS_PENDING, Booking.STATUS_CONFIRMED],
                    check_in_date__lt=check_out,
                    check_out_date__gt=check_in
                )
                if self.instance:
                    overlapping_bookings = overlapping_bookings.exclude(booking_id=self.instance.booking_id)
                
                if overlapping_bookings.exists():
                    raise serializers.ValidationError({
                        "dates": "The listing is not available for the selected dates."
                    })

        return data

    def create(self, validated_data):
        listing = validated_data['listing']
        check_in = validated_data['check_in_date']
        check_out = validated_data['check_out_date']
        
        duration = (check_out - check_in).days
        validated_data['total_price'] = listing.price_per_night * duration
        
        return super().create(validated_data)


class ReviewSerializer(serializers.ModelSerializer):
    listing = ListingSerializer(read_only=True)
    listing_id = serializers.PrimaryKeyRelatedField(
        queryset=Listing.objects.all(), 
        source='listing', 
        write_only=True
    )
    reviewer = UserSerializer(read_only=True)
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), 
        source='reviewer', 
        write_only=True
    )
    rating_display = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            'review_id', 'listing', 'listing_id', 'reviewer', 'reviewer_id',
            'rating', 'rating_display', 'comment', 'created_at', 'updated_at'
        ]
        read_only_fields = ['review_id', 'created_at', "'updated_at"]

    def get_rating_display(self, obj):
        return obj.get_rating_display()

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

    def validate(self, data):
        listing = data.get('listing')
        reviewer = data.get('reviewer')
        
        if self.instance is None:
            completed_booking = Booking.objects.filter(
                listing=listing,
                guest=reviewer,
                status=Booking.STATUS_COMPLETED
            ).exists()
            
            if not completed_booking:
                raise serializers.ValidationError({
                    "reviewer": "You can only review listings you've booked and completed."
                })

            existing_review = Review.objects.filter(
                listing=listing,
                reviewer=reviewer
            ).exists()
            
            if existing_review:
                raise serializers.ValidationError({
                    "reviewer": "You have already reviewed this listing."
                })

        return data


class PaymentSerializer(serializers.ModelSerializer):
    booking = BookingSerializer(read_only=True)
    booking_id = serializers.PrimaryKeyRelatedField(
        queryset=Booking.objects.all(), 
        source='booking', 
        write_only=True
    )
    
    class Meta:
        model = Payment
        fields = [
            'payment_id', 'booking', 'booking_id', 'amount', 
            'transaction_id', 'reference', 'status', 'payment_method',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['payment_id', 'created_at', 'updated_at']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0.")
        return value

    def validate(self, data):
        booking = data.get('booking')
        amount = data.get('amount')
        
        if booking and amount:
            if amount != booking.total_price:
                raise serializers.ValidationError({
                    "amount": f"Payment amount (${amount}) must match booking total (${booking.total_price})."
                })
        
        return data


# Simplified serializers for specific operations
class ListingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'price_per_night', 'location', 'amenities']


class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['listing_id', 'check_in_date', 'check_out_date']


class PaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['booking_id', 'payment_method']


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['listing_id', 'rating', 'comment']


# Swagger response schemas
listing_response_schema = openapi.Response(
    description="Listing details",
    schema=ListingSerializer
)

booking_response_schema = openapi.Response(
    description="Booking details", 
    schema=BookingSerializer
)

error_response_schema = openapi.Response(
    description="Error response",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'error': openapi.Schema(type=openapi.TYPE_STRING),
            'details': openapi.Schema(type=openapi.TYPE_OBJECT)
        }
    )
)
