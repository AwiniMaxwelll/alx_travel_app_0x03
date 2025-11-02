from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Listing, Booking, Review, Payment 


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class ReviewSerializer(serializers.ModelSerializer):
    reviewer = UserSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ['review_id', 'reviewer', 'rating', 'comment', 'created_at']


class ListingSerializer(serializers.ModelSerializer):
    host = UserSerializer(read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = [
            'listing_id', 'title', 'description', 'price_per_night', 'location',
            'amenities', 'host', 'created_at', 'updated_at', 'is_available',
            'reviews', 'average_rating', 'review_count'
        ]

    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return 0

    def get_review_count(self, obj):
        return obj.reviews.count()


class BookingSerializer(serializers.ModelSerializer):
    listing = ListingSerializer(read_only=True)
    guest = UserSerializer(read_only=True)
    listing_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Booking
        fields = [
            'booking_id', 'listing', 'listing_id', 'guest', 'check_in_date',
            'check_out_date', 'total_price', 'status', 'created_at'
        ]

    def validate(self, data):
        if data['check_in_date'] >= data['check_out_date']:
            raise serializers.ValidationError("Check-out date must be after check-in date.")
        return data


class PaymentSerializer(serializers.ModelSerializer):  
    booking = BookingSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = [
            'payment_id', 'booking', 'amount', 'transaction_id', 'reference',
            'status', 'payment_method', 'created_at', 'updated_at'
        ]
        read_only_fields = ['payment_id', 'created_at', 'updated_at']