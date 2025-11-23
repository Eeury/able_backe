from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    User, Post, PostLike, Comment, Job, JobBid,
    Service, Appointment, Chat, Message, ServiceReview
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User Admin"""
    list_display = ['username', 'email', 'user_type', 'disability_type', 'is_verified', 'join_date', 'is_active']
    list_filter = ['user_type', 'disability_type', 'service_type', 'is_verified', 'is_active', 'join_date']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-join_date']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('user_type', 'disability_type', 'service_type', 'avatar', 'is_verified')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('user_type', 'disability_type', 'service_type')
        }),
    )
    
    actions = ['verify_users', 'initiate_admin_chat']
    
    def verify_users(self, request, queryset):
        """Verify selected users"""
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} users were successfully verified.')
    verify_users.short_description = "Verify selected users"
    
    def initiate_admin_chat(self, request, queryset):
        """Initiate admin chat with selected users"""
        for user in queryset:
            # Create or get existing chat
            existing_chat = Chat.objects.filter(
                participants=request.user
            ).filter(
                participants=user
            ).filter(
                participants__count=2
            ).first()
            
            if not existing_chat:
                chat = Chat.objects.create()
                chat.participants.add(request.user, user)
                
                # Send initial admin message
                Message.objects.create(
                    chat=chat,
                    sender=request.user,
                    content=f"Hello {user.username}, this is an admin message. How can we help you today?"
                )
        
        self.message_user(request, f'Admin chats initiated with {queryset.count()} users.')
    initiate_admin_chat.short_description = "Initiate admin chat with selected users"


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Post Admin"""
    list_display = ['id', 'author', 'content_preview', 'likes_count', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at', 'author__user_type']
    search_fields = ['content', 'author__username']
    ordering = ['-created_at']
    readonly_fields = ['likes_count', 'created_at', 'updated_at']
    
    actions = ['deactivate_posts', 'activate_posts']
    
    def content_preview(self, obj):
        """Show preview of post content"""
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content Preview'
    
    def deactivate_posts(self, request, queryset):
        """Deactivate selected posts"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} posts were deactivated.')
    deactivate_posts.short_description = "Deactivate selected posts"
    
    def activate_posts(self, request, queryset):
        """Activate selected posts"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} posts were activated.')
    activate_posts.short_description = "Activate selected posts"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Comment Admin"""
    list_display = ['id', 'author', 'post', 'content_preview', 'created_at']
    list_filter = ['created_at', 'author__user_type']
    search_fields = ['content', 'author__username']
    ordering = ['-created_at']
    
    def content_preview(self, obj):
        """Show preview of comment content"""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    """Job Admin"""
    list_display = ['id', 'title', 'category', 'posted_by', 'budget', 'bids_count', 'created_at', 'is_active']
    list_filter = ['category', 'is_active', 'created_at', 'posted_by__user_type']
    search_fields = ['title', 'description', 'posted_by__username']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    actions = ['deactivate_jobs', 'activate_jobs']
    
    def bids_count(self, obj):
        """Show number of bids"""
        return obj.bids.count()
    bids_count.short_description = 'Bids Count'
    
    def deactivate_jobs(self, request, queryset):
        """Deactivate selected jobs"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} jobs were deactivated.')
    deactivate_jobs.short_description = "Deactivate selected jobs"
    
    def activate_jobs(self, request, queryset):
        """Activate selected jobs"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} jobs were activated.')
    activate_jobs.short_description = "Activate selected jobs"


@admin.register(JobBid)
class JobBidAdmin(admin.ModelAdmin):
    """Job Bid Admin"""
    list_display = ['id', 'job', 'bidder', 'amount', 'is_accepted', 'created_at']
    list_filter = ['is_accepted', 'created_at']
    search_fields = ['job__title', 'bidder__username']
    ordering = ['-created_at']


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """Service Admin"""
    list_display = ['id', 'title', 'specialty', 'provider', 'rating', 'price_per_session', 'created_at', 'is_active']
    list_filter = ['specialty', 'is_active', 'created_at', 'provider__user_type']
    search_fields = ['title', 'description', 'provider__username', 'location']
    ordering = ['-rating', '-created_at']
    readonly_fields = ['rating', 'created_at', 'updated_at']
    
    actions = ['deactivate_services', 'activate_services']
    
    def deactivate_services(self, request, queryset):
        """Deactivate selected services"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} services were deactivated.')
    deactivate_services.short_description = "Deactivate selected services"
    
    def activate_services(self, request, queryset):
        """Activate selected services"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} services were activated.')
    activate_services.short_description = "Activate selected services"


@admin.register(ServiceReview)
class ServiceReviewAdmin(admin.ModelAdmin):
    """Service Review Admin"""
    list_display = ['id', 'service', 'reviewer', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['service__title', 'reviewer__username']
    ordering = ['-created_at']


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    """Appointment Admin"""
    list_display = ['id', 'service', 'client', 'appointment_date', 'status', 'created_at']
    list_filter = ['status', 'appointment_date', 'created_at']
    search_fields = ['service__title', 'client__username']
    ordering = ['appointment_date']


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    """Chat Admin"""
    list_display = ['id', 'participants_list', 'messages_count', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['participants__username']
    ordering = ['-updated_at']
    
    def participants_list(self, obj):
        """Show list of participants"""
        return ", ".join([user.username for user in obj.participants.all()])
    participants_list.short_description = 'Participants'
    
    def messages_count(self, obj):
        """Show number of messages"""
        return obj.messages.count()
    messages_count.short_description = 'Messages Count'
    
    actions = ['initiate_admin_chat_with_participants']
    
    def initiate_admin_chat_with_participants(self, request, queryset):
        """Initiate admin chat with all participants of selected chats"""
        initiated_count = 0
        for chat in queryset:
            for participant in chat.participants.exclude(id=request.user.id):
                # Create or get existing chat with admin
                existing_chat = Chat.objects.filter(
                    participants=request.user
                ).filter(
                    participants=participant
                ).filter(
                    participants__count=2
                ).first()
                
                if not existing_chat:
                    admin_chat = Chat.objects.create()
                    admin_chat.participants.add(request.user, participant)
                    
                    # Send initial admin message
                    Message.objects.create(
                        chat=admin_chat,
                        sender=request.user,
                        content=f"Hello {participant.username}, this is an admin message regarding your recent activity."
                    )
                    initiated_count += 1
        
        self.message_user(request, f'Admin chats initiated with {initiated_count} users.')
    initiate_admin_chat_with_participants.short_description = "Initiate admin chat with participants"


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Message Admin"""
    list_display = ['id', 'chat', 'sender', 'content_preview', 'created_at', 'is_read']
    list_filter = ['is_read', 'created_at', 'sender__user_type']
    search_fields = ['content', 'sender__username']
    ordering = ['-created_at']
    
    def content_preview(self, obj):
        """Show preview of message content"""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'


# Customize admin site
admin.site.site_header = "Able Connect Admin"
admin.site.site_title = "Able Connect Admin Portal"
admin.site.index_title = "Welcome to Able Connect Administration"