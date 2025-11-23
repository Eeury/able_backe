from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """Custom User model that extends Django's AbstractUser"""
    USER_TYPE_CHOICES = [
        ('pwd', 'Person with Disability'),
        ('client', 'Client'),
        ('doctor', 'Doctor/Therapist'),
        ('trainer', 'Trainer'),
        ('admin', 'Admin'),
    ]
    
    DISABILITY_TYPE_CHOICES = [
        ('hearing', 'Hearing'),
        ('visual', 'Visual'),
        ('physical', 'Physical'),
        ('intellectual', 'Intellectual'),
        ('autism', 'Autism'),
        ('learning', 'Learning Disabilities'),
        ('psychological', 'Psychological'),
    ]
    
    SERVICE_TYPE_CHOICES = [
        ('freelance', 'Freelance Jobs'),
        ('medical', 'Medical Services'),
    ]
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='pwd')
    disability_type = models.CharField(max_length=20, choices=DISABILITY_TYPE_CHOICES, blank=True, null=True)
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPE_CHOICES, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)  # Phone number
    avatar = models.CharField(max_length=1, blank=True)  # Single character for avatar
    join_date = models.DateTimeField(default=timezone.now)
    is_verified = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        # Auto-generate avatar from first letter of first name or username
        if not self.avatar and (self.first_name or self.username):
            self.avatar = (self.first_name or self.username)[0].upper()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"


class Post(models.Model):
    """Model for user posts in the feed"""
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    likes_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)  # For soft delete by admin
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Post by {self.author.username} at {self.created_at}"


class PostLike(models.Model):
    """Model to track post likes"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ('user', 'post')
    
    def __str__(self):
        return f"{self.user.username} likes {self.post.id}"


class Comment(models.Model):
    """Model for post comments"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.author.username} on post {self.post.id}"


class Job(models.Model):
    """Model for freelance job postings"""
    CATEGORY_CHOICES = [
        ('design', 'Design'),
        ('writing', 'Writing'),
        ('programming', 'Programming'),
        ('consulting', 'Consulting'),
        ('marketing', 'Marketing'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField()
    budget = models.CharField(max_length=100)  # e.g., "$500 - $1000"
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_jobs')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    deadline = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} by {self.posted_by.username}"


class JobBid(models.Model):
    """Model for job bids"""
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='bids')
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_bids')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    proposal = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    is_accepted = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('job', 'bidder')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Bid by {self.bidder.username} on {self.job.title}"


class Service(models.Model):
    """Model for medical/professional services"""
    SPECIALTY_CHOICES = [
        ('physical_therapist', 'Physical Therapist'),
        ('occupational_therapist', 'Occupational Therapist'),
        ('speech_therapist', 'Speech Therapist'),
        ('sign_therapist', 'Sign Language Therapist'),
        ('mental_health_counselor', 'Mental Health Counselor'),
        ('disability_specialist', 'Disability Specialist'),
        ('caregiver', 'Caregiver'),
        ('personal_assistant', 'Personal Assistant'),
        ('other', 'Other'),
    ]
    
    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='services')
    title = models.CharField(max_length=200)
    specialty = models.CharField(max_length=30, choices=SPECIALTY_CHOICES)
    description = models.TextField()
    experience_years = models.PositiveIntegerField()
    location = models.CharField(max_length=200)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    price_per_session = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    availability = models.CharField(max_length=200)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-rating', '-created_at']
    
    def __str__(self):
        return f"{self.title} by {self.provider.username}"


class Appointment(models.Model):
    """Model for service appointments"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='appointments')
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    appointment_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['appointment_date']
    
    def __str__(self):
        return f"Appointment: {self.client.username} with {self.service.provider.username}"


class Chat(models.Model):
    """Model for chat conversations"""
    participants = models.ManyToManyField(User, related_name='chats')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        participant_names = ", ".join([user.username for user in self.participants.all()[:2]])
        return f"Chat: {participant_names}"


class Message(models.Model):
    """Model for chat messages"""
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Message from {self.sender.username} in chat {self.chat.id}"


class ServiceReview(models.Model):
    """Model for service reviews and ratings"""
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='service_reviews')
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 stars
    review_text = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ('service', 'reviewer')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review by {self.reviewer.username} for {self.service.title}"