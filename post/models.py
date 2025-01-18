from django.db import models
from django.db.models import (
        CharField, DateTimeField, ForeignKey,
        PositiveIntegerField, TextField,
        ManyToManyField, ImageField
        )
from shared.validators import check_vulgarity
# Create your models here.

class Commentable(models.Model):
    text = TextField(validators=[check_vulgarity], null=False, blank=False)
    created_at = DateTimeField(auto_now_add=True)
    likes = PositiveIntegerField(default=0)
    comments = PositiveIntegerField(default=0)
    views = PositiveIntegerField(default=0)
    
    class Meta:
        abstract = True


class Post(Commentable):
    user = ForeignKey('user.User', on_delete=models.CASCADE, related_name='posts')
    image = ImageField(null=True, upload_to='Images/')
    
    def __repr__(self):
        return '<{}> {}'.format(self.__class__.__name__, self.__dict__)

class Comment(Commentable):
    user = ForeignKey('user.User', on_delete=models.DO_NOTHING)
    post = ForeignKey('Post', related_name='replies_to', on_delete=models.CASCADE)


class Reply(Comment):
    parent = ForeignKey('Comment', on_delete=models.CASCADE, related_name='replies_to')
