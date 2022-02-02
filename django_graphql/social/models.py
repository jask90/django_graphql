from django.contrib.auth.models import User
from django.db import models


class Idea(models.Model):
    VISIBILITY_CHOICES = (
        ('public', u'Public'),
        ('protected', u'Protected'),
        ('private', u'Private'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=u'user')
    text = models.CharField(max_length=140, verbose_name=u'text')
    visibility = models.CharField(max_length=25, default='private', choices=VISIBILITY_CHOICES, verbose_name='visibility')
    created = models.DateTimeField(auto_now_add=True, verbose_name=u'creation date')
    modified = models.DateTimeField(auto_now=True, verbose_name=u'modification date')

    class Meta:
        verbose_name = 'Idea'
        verbose_name_plural = 'Ideas'

    def __str__(self):
        return f'{self.user.email} - {self.visibility}'
    

class Follow(models.Model):
    STATUS_CHOICES = (
        ('pending', u'Pending Approval'),
        ('accepted', u'Accepted'),
        ('rejected', u'Rejected'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user', verbose_name=u'user')
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower', verbose_name=u'follower')
    status = models.CharField(max_length=25, default='pending', choices=STATUS_CHOICES, verbose_name='status')
    created = models.DateTimeField(auto_now_add=True, verbose_name=u'creation date')
    modified = models.DateTimeField(auto_now=True, verbose_name=u'modification date')

    class Meta:
        unique_together = (("user", "follower"),)
        verbose_name = 'Follow'
        verbose_name_plural = 'Follows'

    def __str__(self):
        return f'{self.user.email} - {self.follower.email} - {self.status}'

    def accept(self, user):
        if self.user == user:
            self.status = 'accepted'
            self.save()
            return True
        else:
            return False

    def refuse(self, user):
        if self.user == user:
            self.delete()
            return True
        else:
            return False
