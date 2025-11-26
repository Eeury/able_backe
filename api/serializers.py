from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import (
    User, Post, PostLike, Comment, Job, JobBid, 
    Service, Appointment, Chat, Message, ServiceReview
)


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'user_type', 'disability_type', 'service_type', 'avatar',
            'join_date', 'is_verified', 'password', 'confirm_password'
        ]
        read_only_fields = ['id', 'join_date', 'avatar']
    
    def validate(self, attrs):
        if attrs.get('password') != attrs.get('confirm_password'):
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile (without sensitive data)"""
    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name',
            'user_type', 'disability_type', 'service_type', 
            'avatar', 'join_date', 'is_verified'
        ]
        read_only_fields = ['id', 'join_date', 'avatar']


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    email = serializers.EmailField()
    password = serializers.CharField()
    user_type = serializers.ChoiceField(choices=User.USER_TYPE_CHOICES)
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        user_type = attrs.get('user_type')
        
        if email and password:
            # Handle potential duplicate users with same email
            users = User.objects.filter(email=email, user_type=user_type)
            
            if users.exists():
                user = None
                # Check each user to see if password matches
                for u in users:
                    if u.check_password(password):
                        user = u
                        break
                
                if user:
                    if not user.is_active:
                        raise serializers.ValidationError('User account is disabled.')
                    attrs['user'] = user
                    return attrs
                else:
                    raise serializers.ValidationError('Invalid credentials.')
            else:
                raise serializers.ValidationError('Invalid credentials.')
        else:
            raise serializers.ValidationError('Must include email and password.')


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment model"""
    author = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'author', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']


class PostSerializer(serializers.ModelSerializer):
    """Serializer for Post model"""
    author = UserProfileSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'author', 'content', 'created_at', 'updated_at',
            'likes_count', 'comments', 'is_liked', 'is_active'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'likes_count']
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return PostLike.objects.filter(user=request.user, post=obj).exists()
        return False


class PostLikeSerializer(serializers.ModelSerializer):
    """Serializer for PostLike model"""
    class Meta:
        model = PostLike
        fields = ['id', 'user', 'post', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class JobBidSerializer(serializers.ModelSerializer):
    """Serializer for JobBid model"""
    bidder = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = JobBid
        fields = ['id', 'bidder', 'amount', 'proposal', 'created_at', 'is_accepted']
        read_only_fields = ['id', 'created_at']


class JobSerializer(serializers.ModelSerializer):
    """Serializer for Job model"""
    posted_by = UserProfileSerializer(read_only=True)
    bids = JobBidSerializer(many=True, read_only=True)
    bids_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Job
        fields = [
            'id', 'title', 'category', 'description', 'budget',
            'posted_by', 'created_at', 'updated_at', 'is_active',
            'deadline', 'bids', 'bids_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_bids_count(self, obj):
        return obj.bids.count()


class ServiceReviewSerializer(serializers.ModelSerializer):
    """Serializer for ServiceReview model"""
    reviewer = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = ServiceReview
        fields = ['id', 'reviewer', 'rating', 'review_text', 'created_at']
        read_only_fields = ['id', 'created_at']


class ServiceSerializer(serializers.ModelSerializer):
    """Serializer for Service model"""
    provider = UserProfileSerializer(read_only=True)
    reviews = ServiceReviewSerializer(many=True, read_only=True)
    reviews_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Service
        fields = [
            'id', 'title', 'specialty', 'description', 'experience_years',
            'location', 'rating', 'price_per_session', 'availability',
            'provider', 'created_at', 'updated_at', 'is_active',
            'reviews', 'reviews_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'rating']
    
    def get_reviews_count(self, obj):
        return obj.reviews.count()


class AppointmentSerializer(serializers.ModelSerializer):
    """Serializer for Appointment model"""
    service = ServiceSerializer(read_only=True)
    client = UserProfileSerializer(read_only=True)
    service_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'service', 'service_id', 'client', 'appointment_date',
            'status', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model"""
    sender = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'sender', 'content', 'created_at', 'is_read']
        read_only_fields = ['id', 'created_at']


class ChatSerializer(serializers.ModelSerializer):
    """Serializer for Chat model"""
    participants = UserProfileSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Chat
        fields = [
            'id', 'participants', 'created_at', 'updated_at',
            'is_active', 'last_message', 'unread_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_last_message(self, obj):
        last_message = obj.messages.last()
        if last_message:
            return MessageSerializer(last_message).data
        return None
    
    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.messages.filter(is_read=False).exclude(sender=request.user).count()
        return 0


class ChatDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for Chat with messages"""
    participants = UserProfileSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Chat
        fields = [
            'id', 'participants', 'messages', 'created_at',
            'updated_at', 'is_active'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
