from django.db import models
from django.db.models import (
        CharField, DateTimeField, ForeignKey,
        PositiveIntegerField, TextField,
        ManyToManyField, ImageField, Q, CheckConstraint
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
    user = ForeignKey('user.User', on_delete=models.CASCADE)
    post = ForeignKey('Post', null=True, default=None, related_name='replies_to', on_delete=models.CASCADE)
    parent_comment = ForeignKey('self', null=True, default=None,  on_delete=models.CASCADE, related_name='replies_to')
   
    class Meta:
            constraints = [
                CheckConstraint(
                    check=((Q(post__isnull=True) & Q(parent_comment__isnull=False))
                        | (Q(post__isnull=False) & Q(parent_comment__isnull=True))),
                    name='at_least_one_parent'
                    )
                ]
      

    def __repr__(self):
        return '<{}> {}'.format(self.__class__.__name__, self.__dict__)
