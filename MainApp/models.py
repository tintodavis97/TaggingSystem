from django.db import models
from django.contrib.auth import get_user_model

from TaggingSystem import settings

User = get_user_model()


class PostModel(models.Model):
    created_on = models.DateTimeField(auto_now_add=True, editable=False)
    description = models.TextField()


class Tag(models.Model):
    tag = models.CharField(max_length=128, unique=True)


class PostImageMapping(models.Model):
    post = models.ForeignKey(PostModel, related_name='post_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=settings.MEDIA_ROOT)


class PostTagMapping(models.Model):
    post = models.ForeignKey(PostModel, related_name='post_tags', on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, null=True, blank=True)


class PostLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(PostModel, on_delete=models.CASCADE)
    like = models.BooleanField(null=True, blank=True)


class TagWeight(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    weight = models.IntegerField(default=0)
