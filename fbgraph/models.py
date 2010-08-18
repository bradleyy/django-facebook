from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

# Create your models here.
class FBUser(models.Model):
    user = models.ForeignKey(User, unique=True)
    uid = models.CharField(max_length=25, unique=True, db_index=True)
    name = models.CharField(max_length=256)
    profile_url = models.CharField(max_length=512)
    access_token = models.CharField(max_length=512)
    def authenticate(self):
        return authenticate(uid=self.uid)
