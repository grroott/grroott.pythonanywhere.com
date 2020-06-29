from django.urls import path
from .views import (
    PostListView,
    PostDetailView,
    PostCreateView,
    PostUpdateView,
    PostDeleteView,
    UserPostListView
)
from . import views

urlpatterns = [
    path('', PostListView.as_view(), name='blog-home'),
    path('user/<str:username>/', UserPostListView.as_view(), name='user-posts'),
    path('user/<str:username>/followers/', UserPostListView.as_view(template_name='blog/followers.html'), name='followers'),
    path('user/<str:username>/following/', UserPostListView.as_view(template_name='blog/following.html'), name='following'),
    path('post/<int:pk>/likes/', PostDetailView.as_view(template_name='blog/post_detail_likes.html'), name='post-detail-likes'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/new/', PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('about/', views.about, name='blog-about'),
    path('likes/', views.like_post, name='like-post'),
    path('search/', views.search, name='search'),
    path('most-liked-posts/', views.most_liked_posts, name='most-liked-posts'),
]
