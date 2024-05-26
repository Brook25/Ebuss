from django.db import models

# Create your models here.

class Comment(models.Model):
    user = ForeignKey('User', on_delete=models.DO_NOTHING)
    text = TextField(validators=[vulgarity_validator])
    timestamp = DateTimeField(auto_now_add=True)
    likes = PositiveIntegerField()
    comments = PositiveIntegerField()
    views = PositiveIntegerField()
    post = ManyToOneField('Comment', related_name='replies_to')

    def __repr__(self):
        return '<{}> {}'.format(self.__class__name, self.__dict__)

class Post(Comment):
    user = ForeignKey('User', on_delete=models.CASCADE, related_name='posts')
    image = ImageField(null=True, upload_to='Images/')
