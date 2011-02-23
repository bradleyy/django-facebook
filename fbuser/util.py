from django.conf import settings
from django.contrib.auth.models import User
from fbuser.models import FBUser
import facebook

def same_auth(request, session):
    graph = session.get('fbgraph')
    fbcookie = request.session.get('fbuser', None)
    if not graph or not fbcookie:
        return False
    else:
        return fbcookie.get("access_token", None) == getattr(graph, 'access_token', None)

def get_next(request):
    if request.GET.has_key('next'):
        next = request.GET['next']
    else:
        if settings.FB_AFTERLOGIN:
            next = settings.FB_AFTERLOGIN
        else:
            next = "/"
    return next

def get_fb_cookie(request):
    return facebook.get_user_from_cookie(
            request.COOKIES, settings.FACEBOOK_API_KEY,
            settings.FACEBOOK_SECRET_KEY)

def email_match(request):
    try:
        profile = request.session.get['fbprofile']
        if profile:
            User.objects.get(email=profile['email'])
            return True
        else:
            return False
    except:
        return False

def fb_id_username_match(request):
    #TODO: I think this is actually a bad idea-- they either have an fbuser or not.
    #TODO: if they have an fbuser, then done.
    #TODO: make sure that when FBUser creates User object, that it uses get_or_create
    try:
        profile = request.session.get['fbprofile']
        if profile:
            User.objects.get(username=profile['id'])
            return True
        else:
            return False
    except:
        return False

def existing_fbuser(cookie):
    try:
        fb_user = FBUser.objects.get(uid=cookie["uid"])
        return fb_user
    except:
        return None
