from django.db import models

# Create your models here.

class Comment(models.Model):
    user = ForeignKey('User', on_delete=models.DO_NOTHING)
    text = TextField(validators=[vulgarity_validator])
    timestamp = DateTimeField(auto_now_add=True)
    likes = PositiveIntegerField()

    def __repr__(self):
        return '<{}> {}'.format(self.__class__name, self.__dict__)

class Reply(Comment):
   comment = ForeignKey('Comment', on_delete=models.CASCADE, related_name='replies_to')
   reply_to = ForeignKey('User', null=True, on_delete=models.DO_NOTHING)

class Post(Comment):
    #user = ForeignKey('User', on_delete=models.CASCADE, related_name='posts')
    image = ImageField(null=True, upload_to='Images/')
