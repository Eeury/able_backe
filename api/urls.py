from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # Authentication URLs
    path('auth/register/', views.register, name='register'),
    path('auth/login/', views.login, name='login'),
    path('auth/logout/', views.logout, name='logout'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/profile/', views.profile, name='profile'),
    path('auth/profile/update/', views.update_profile, name='update_profile'),
    
    # Post URLs
    path('posts/', views.PostListCreateView.as_view(), name='post-list-create'),
    path('posts/<int:pk>/', views.PostDetailView.as_view(), name='post-detail'),
    path('posts/<int:post_id>/like/', views.toggle_like, name='toggle-like'),
    path('posts/<int:post_id>/comments/', views.CommentListCreateView.as_view(), name='comment-list-create'),
    
    # Job URLs
    path('jobs/', views.JobListCreateView.as_view(), name='job-list-create'),
    path('jobs/<int:pk>/', views.JobDetailView.as_view(), name='job-detail'),
    path('jobs/<int:job_id>/bids/', views.JobBidListCreateView.as_view(), name='job-bid-list-create'),
    
    # Service URLs
    path('services/', views.ServiceListCreateView.as_view(), name='service-list-create'),
    path('services/<int:pk>/', views.ServiceDetailView.as_view(), name='service-detail'),
    path('services/<int:service_id>/reviews/', views.ServiceReviewListCreateView.as_view(), name='service-review-list-create'),
    
    # Appointment URLs
    path('appointments/', views.AppointmentListCreateView.as_view(), name='appointment-list-create'),
    path('appointments/<int:pk>/', views.AppointmentDetailView.as_view(), name='appointment-detail'),
    
    # Chat URLs
    path('chats/', views.ChatListView.as_view(), name='chat-list'),
    path('chats/<int:pk>/', views.ChatDetailView.as_view(), name='chat-detail'),
    path('chats/create/', views.create_or_get_chat, name='create-or-get-chat'),
    path('chats/<int:chat_id>/messages/', views.MessageCreateView.as_view(), name='message-create'),
    
    # Admin URLs
    path('admin/stats/', views.admin_stats, name='admin-stats'),
    path('admin/posts/<int:post_id>/delete/', views.admin_delete_post, name='admin-delete-post'),
    path('admin/jobs/<int:job_id>/delete/', views.admin_delete_job, name='admin-delete-job'),
    path('admin/services/<int:service_id>/delete/', views.admin_delete_service, name='admin-delete-service'),
    path('admin/chat/initiate/', views.admin_initiate_chat, name='admin-initiate-chat'),
]
