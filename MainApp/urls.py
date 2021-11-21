from django.urls import include, path
from rest_framework.routers import SimpleRouter
from MainApp import views
router = SimpleRouter()

router.register('create-user', views.UserCreationViewSet, basename='create-user')

urlpatterns = [
    path('', include(router.urls)),
    path('create-posts', views.create_post, name='create-posts'),
    path('create-tags', views.create_tag, name='create-tags'),
    path('like-post', views.post_like, name='like-post'),
    path('dislike-post', views.post_dislike, name='dislike-post'),
    path('posts', views.get_posts, name='posts'),
    path('post/<int:pk>', views.get_post, name='post'),
    path('get-liked-users/<int:pk>', views.get_liked_users, name='get_liked_users')
]