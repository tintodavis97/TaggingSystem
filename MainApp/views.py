from django.db.models import F
from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework import viewsets, permissions, status

from MainApp.models import PostModel, PostImageMapping, PostTagMapping, Tag, PostLike, TagWeight
from MainApp.serializers import CreateUserProfileSerializer

User = get_user_model()


class UserCreationViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = CreateUserProfileSerializer
    permission_classes = [
        permissions.AllowAny
    ]


@api_view(['POST'])
def create_post(request):
    '''
    This api is used to create new post,
    post_data :{
    "tags": 1,2,
    "description": "Cat Person",
    "images": [images]
    '''
    data = request.data
    if not request.user.is_superuser:
        raise ValidationError('Admin Can Only Create Post')
    description = data.get('description', None)
    tags = data.get('tags', None)
    if not description:
        raise ValidationError('Description Must Provide')
    obj = PostModel.objects.create(description=description)
    images = dict((data).lists())['images']
    for image in images:
        img_mapping_obj = PostImageMapping.objects.create(image=image, post=obj)
    if tags:
        tags = tags.split(',')
        for tag in tags:
            tag_mapping_obj = PostTagMapping.objects.get_or_create(tag_id=tag, post=obj)

    return Response('Post Successfully Created')


@api_view(['POST'])
def create_tag(request):
    '''
    This api is used to create new tag,
    post_data :{
    "tag": "Cat"
    }
    '''
    data = request.data
    tag = data.get('tag', None)
    if not tag:
        raise ValidationError('Tag Must Provide')
    obj = Tag.objects.get_or_create(tag=tag)

    return Response('Tag Successfully Created')


@api_view(['POST'])
def tag_mapping(request):
    '''
    This api is used to map tags to post,
    post_data :{
    "tags": 1,2,
    "post": 1
    }
    '''
    data = request.data
    tags = data.get('tags', None)
    post = data.get('post', None)
    if not post:
        raise ValidationError('Post Must Provide')
    if tags:
        tags = tags.split(',')
        for tag in tags:
            obj = PostTagMapping.objects.get_or_create(post_id=post, tag_id=tag)


@api_view(['POST'])
def post_like(request):
    '''
    This api is used to like a post,
    post_data :{
    "post": 1
    }
    '''
    data = request.data
    post = data.get('post', None)

    if not post:
        raise ValidationError('Post Must Provide')
    obj, created = PostLike.objects.get_or_create(post_id=post, user=request.user)
    obj.like = True
    obj.save()
    tags = PostTagMapping.objects.filter(post=obj.post).values_list('tag', flat=True)
    for tag in tags:
        tag_weight_obj, created = TagWeight.objects.get_or_create(user=request.user, tag_id=tag)
        tag_weight_obj.weight += 1
        tag_weight_obj.save()
    return Response('Post Liked')


@api_view(['POST'])
def post_dislike(request):
    '''
    This api is used to dislike a post,
    post_data :{
    "post": 1
    }
    '''
    data = request.data
    post = data.get('post', None)

    if not post:
        raise ValidationError('Post Must Provide')
    obj, created = PostLike.objects.get_or_create(post_id=post, user=request.user)
    obj.like = False
    obj.save()
    tags = PostTagMapping.objects.filter(post=obj.post).values_list('tag', flat=True)
    for tag in tags:
        tag_weight_obj, created = TagWeight.objects.get_or_create(user=request.user, tag_id=tag)
        tag_weight_obj.weight -= 1
        tag_weight_obj.save()
    return Response('Post Disliked')


@api_view(['GET'])
def get_posts(request):
    '''
    This api is used to get posts,
    '''
    query_params = request.query_params
    off_set = query_params.get('off_set', 0)
    limit = query_params.get('limit', 5)

    return_data = []
    posts = PostModel.objects.all().order_by('-post_tags__tag__tagweight__weight')[off_set:off_set + limit]
    for post in posts:
        tags = list(post.post_tags.values())
        images = list(post.post_images.values())
        like = PostLike.objects.filter(user=request.user, post=post).first()
        likes = PostLike.objects.filter(user=request.user, post=post, like=True).count()
        dislikes = PostLike.objects.filter(user=request.user, post=post, like=False).count()

        data = {
            'id': post.id,
            'created_on': post.created_on,
            'description': post.description,
            'tags': tags,
            'images': images,
            'like': like.like if like else '',
            'likes': likes,
            'dislikes': dislikes
        }
        return_data.append(data)
    return Response({"posts": return_data})


@api_view(['GET'])
def get_post(request, pk):
    '''
    This api is used to get single post,
    '''
    if not request.user.is_superuser:
        raise ValidationError('Admin Can Only Access')
    try:
        post = PostModel.objects.get(pk=pk)
    except PostModel.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    tags = list(post.post_tags.values())
    images = list(post.post_images.values())
    like = PostLike.objects.filter(user=request.user, post=post).first()
    likes = PostLike.objects.filter(user=request.user, post=post, like=True).count()
    dislikes = PostLike.objects.filter(user=request.user, post=post, like=False).count()

    data = {
        'id': post.id,
        'created_on': post.created_on,
        'description': post.description,
        'tags': tags,
        'images': images,
        'like': like.like if like else '',
        'likes': likes,
        'dislikes': dislikes
    }
    return Response(data)


@api_view(['GET'])
def get_liked_users(request, pk):
    '''
    This api is used to get users name who like the post,
    '''
    try:
        post = PostModel.objects.get(pk=pk)
    except PostModel.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    users = PostLike.objects.filter(post=post, like=True).annotate(user_name=F('user__username')).values('user_name')

    return Response(users)
