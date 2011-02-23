from django.contrib.auth.backends import ModelBackend
from fbuser.models import FBUser

class FBAuthBackend(ModelBackend):

    def authenticate(self, uid=None):
        try:
            fbuser = FBUser.objects.get(uid=uid)
            return fbuser.user 
        except FBUser.DoesNotExist:
            return None
        return None

