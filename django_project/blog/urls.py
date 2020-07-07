from django.urls import path
from .views import (
    PostListView,
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
    path('post/<int:pk>/likes/', views.post_detail_likes, name='post-detail-likes'),
    path('post/new/', PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('about/', views.about, name='blog-about'),
    path('likes/', views.like_post, name='like-post'),
    path('search/', views.search, name='search'),
    path('most-liked-posts/', views.most_liked_posts, name='most-liked-posts'),
    path('most-liked-authors/', views.most_liked_authors, name='most-liked-authors'),
    path('post/<int:pk>/', views.post_detail, name='post-detail'),
]
