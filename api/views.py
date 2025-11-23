from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from django.db.models import Q, Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import (
    User, Post, PostLike, Comment, Job, JobBid,
    Service, Appointment, Chat, Message, ServiceReview
)
from .serializers import (
    UserSerializer, UserProfileSerializer, LoginSerializer,
    PostSerializer, CommentSerializer, PostLikeSerializer,
    JobSerializer, JobBidSerializer, ServiceSerializer,
    AppointmentSerializer, ChatSerializer, ChatDetailSerializer,
    MessageSerializer, ServiceReviewSerializer
)


# Authentication Views
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """User registration endpoint"""
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserProfileSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """User login endpoint"""
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserProfileSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    """Get current user profile"""
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """Update current user profile"""
    serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Post Views
class PostListCreateView(generics.ListCreateAPIView):
    """List all posts or create a new post"""
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['created_at', 'likes_count']
    ordering = ['-created_at']
    search_fields = ['content', 'author__username']
    
    def get_queryset(self):
        return Post.objects.filter(is_active=True)
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a post"""
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Post.objects.filter(is_active=True)
    
    def get_object(self):
        obj = super().get_object()
        # Only author can update/delete their posts
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            if obj.author != self.request.user and not self.request.user.is_staff:
                self.permission_denied(self.request)
        return obj


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_like(request, post_id):
    """Toggle like on a post"""
    post = get_object_or_404(Post, id=post_id, is_active=True)
    like, created = PostLike.objects.get_or_create(user=request.user, post=post)
    
    if not created:
        like.delete()
        post.likes_count = max(0, post.likes_count - 1)
        liked = False
    else:
        post.likes_count += 1
        liked = True
    
    post.save()
    return Response({'liked': liked, 'likes_count': post.likes_count})


class CommentListCreateView(generics.ListCreateAPIView):
    """List comments for a post or create a new comment"""
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        post_id = self.kwargs['post_id']
        return Comment.objects.filter(post_id=post_id, post__is_active=True)
    
    def perform_create(self, serializer):
        post_id = self.kwargs['post_id']
        post = get_object_or_404(Post, id=post_id, is_active=True)
        serializer.save(author=self.request.user, post=post)


# Job Views
class JobListCreateView(generics.ListCreateAPIView):
    """List all jobs or create a new job"""
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'posted_by']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'budget']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Job.objects.filter(is_active=True)
    
    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)


class JobDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a job"""
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Job.objects.filter(is_active=True)
    
    def get_object(self):
        obj = super().get_object()
        # Only job poster can update/delete their jobs
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            if obj.posted_by != self.request.user and not self.request.user.is_staff:
                self.permission_denied(self.request)
        return obj


class JobBidListCreateView(generics.ListCreateAPIView):
    """List bids for a job or create a new bid"""
    serializer_class = JobBidSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        job_id = self.kwargs['job_id']
        return JobBid.objects.filter(job_id=job_id, job__is_active=True)
    
    def perform_create(self, serializer):
        job_id = self.kwargs['job_id']
        job = get_object_or_404(Job, id=job_id, is_active=True)
        serializer.save(bidder=self.request.user, job=job)


# Service Views
class ServiceListCreateView(generics.ListCreateAPIView):
    """List all services or create a new service"""
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['specialty', 'provider']
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['created_at', 'rating', 'price_per_session']
    ordering = ['-rating', '-created_at']
    
    def get_queryset(self):
        return Service.objects.filter(is_active=True)
    
    def perform_create(self, serializer):
        serializer.save(provider=self.request.user)


class ServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a service"""
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Service.objects.filter(is_active=True)
    
    def get_object(self):
        obj = super().get_object()
        # Only service provider can update/delete their services
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            if obj.provider != self.request.user and not self.request.user.is_staff:
                self.permission_denied(self.request)
        return obj


class ServiceReviewListCreateView(generics.ListCreateAPIView):
    """List reviews for a service or create a new review"""
    serializer_class = ServiceReviewSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        service_id = self.kwargs['service_id']
        return ServiceReview.objects.filter(service_id=service_id, service__is_active=True)
    
    def perform_create(self, serializer):
        service_id = self.kwargs['service_id']
        service = get_object_or_404(Service, id=service_id, is_active=True)
        review = serializer.save(reviewer=self.request.user, service=service)
        
        # Update service rating
        avg_rating = service.reviews.aggregate(Avg('rating'))['rating__avg']
        service.rating = round(avg_rating, 2) if avg_rating else 0.0
        service.save()


# Appointment Views
class AppointmentListCreateView(generics.ListCreateAPIView):
    """List user appointments or create a new appointment"""
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering = ['appointment_date']
    
    def get_queryset(self):
        return Appointment.objects.filter(client=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(client=self.request.user)


class AppointmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an appointment"""
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Appointment.objects.filter(
            Q(client=self.request.user) | Q(service__provider=self.request.user)
        )


# Chat Views
class ChatListView(generics.ListAPIView):
    """List user chats"""
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Chat.objects.filter(
            participants=self.request.user,
            is_active=True
        ).distinct()


class ChatDetailView(generics.RetrieveAPIView):
    """Retrieve chat with messages"""
    serializer_class = ChatDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Chat.objects.filter(
            participants=self.request.user,
            is_active=True
        ).distinct()
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Mark messages as read
        instance.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_or_get_chat(request):
    """Create a new chat or get existing chat with another user"""
    other_user_id = request.data.get('user_id')
    if not other_user_id:
        return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    other_user = get_object_or_404(User, id=other_user_id)
    
    # Check if chat already exists
    existing_chat = Chat.objects.filter(
        participants=request.user
    ).filter(
        participants=other_user
    ).filter(
        participants__count=2
    ).first()
    
    if existing_chat:
        serializer = ChatDetailSerializer(existing_chat, context={'request': request})
        return Response(serializer.data)
    
    # Create new chat
    chat = Chat.objects.create()
    chat.participants.add(request.user, other_user)
    
    serializer = ChatDetailSerializer(chat, context={'request': request})
    return Response(serializer.data, status=status.HTTP_201_CREATED)


class MessageCreateView(generics.CreateAPIView):
    """Send a message in a chat"""
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        chat_id = self.kwargs['chat_id']
        chat = get_object_or_404(Chat, id=chat_id, participants=self.request.user, is_active=True)
        message = serializer.save(sender=self.request.user, chat=chat)
        
        # Update chat timestamp
        chat.save()  # This will update the updated_at field
        
        return message


# Admin-specific views for the admin panel
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_stats(request):
    """Get admin dashboard statistics"""
    if not request.user.is_staff:
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    stats = {
        'total_users': User.objects.count(),
        'total_posts': Post.objects.filter(is_active=True).count(),
        'total_jobs': Job.objects.filter(is_active=True).count(),
        'total_services': Service.objects.filter(is_active=True).count(),
        'total_chats': Chat.objects.filter(is_active=True).count(),
    }
    return Response(stats)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def admin_delete_post(request, post_id):
    """Admin endpoint to delete/deactivate a post"""
    if not request.user.is_staff:
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    post = get_object_or_404(Post, id=post_id)
    post.is_active = False
    post.save()
    return Response({'message': 'Post deactivated successfully'})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def admin_delete_job(request, job_id):
    """Admin endpoint to delete/deactivate a job"""
    if not request.user.is_staff:
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    job = get_object_or_404(Job, id=job_id)
    job.is_active = False
    job.save()
    return Response({'message': 'Job deactivated successfully'})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def admin_delete_service(request, service_id):
    """Admin endpoint to delete/deactivate a service"""
    if not request.user.is_staff:
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    service = get_object_or_404(Service, id=service_id)
    service.is_active = False
    service.save()
    return Response({'message': 'Service deactivated successfully'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_initiate_chat(request):
    """Admin endpoint to initiate chat with any user"""
    if not request.user.is_staff:
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    user_id = request.data.get('user_id')
    message_content = request.data.get('message', 'Hello! This is an admin message.')
    
    if not user_id:
        return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    target_user = get_object_or_404(User, id=user_id)
    
    # Create or get existing chat
    existing_chat = Chat.objects.filter(
        participants=request.user
    ).filter(
        participants=target_user
    ).filter(
        participants__count=2
    ).first()
    
    if not existing_chat:
        chat = Chat.objects.create()
        chat.participants.add(request.user, target_user)
    else:
        chat = existing_chat
    
    # Send initial message
    message = Message.objects.create(
        chat=chat,
        sender=request.user,
        content=message_content
    )
    
    return Response({
        'chat_id': chat.id,
        'message': MessageSerializer(message).data
    }, status=status.HTTP_201_CREATED)