from django.conf import settings
import facebook
from django.http import HttpResponseRedirect
from fbuser.models import FBUser
from django.core.urlresolvers import reverse
from django.contrib.auth import login, logout
from urllib import quote

class LazyFBGraph(object):
    def __get__(self, request, obj_type=None):
        session = request.session
        if not hasattr(session, '_cached_fbgraph') or not session._cached_fbgraph:
            try:
                session._cached_fbgraph = facebook.GraphAPI(request.fbcookie["access_token"])
            except:
                return None
        return session._cached_fbgraph

class LazyFBProfile(object):
    def __get__(self, request, obj_type=None):
        session = request.session
        if not hasattr(session, '_cached_fbprofile') or not session._cached_fbprofile:
            try:
                session._cached_fbprofile = facebook.GraphAPI(request.fbcookie["access_token"]).get_object("me")
            except:
                return None
        return session._cached_fbprofile

class FBProfile:
    def process_request(self, request):
        cookie = facebook.get_user_from_cookie(
            request.COOKIES, settings.FACEBOOK_API_KEY,
            settings.FACEBOOK_SECRET_KEY)
        if not cookie:
            if request.user.is_authenticated():
                try:

                    #Doing a get on a key that does not exist will
                    #cause an exception: no match, no logout.
                    fbuser = FBUser.objects.get(user__username=request.user.username)
                    logout(request)
                except:
                    pass
            return None
        request.fbcookie = cookie
        session = request.session
        if not hasattr(session, '_cached_fbgraph') or not session._cached_fbgraph:
            try:
                session._cached_fbgraph = facebook.GraphAPI(request.fbcookie["access_token"])
                session._cached_fbprofile = session._cached_fbgraph.get_object("me")
            except:
                session._cached_fbgraph = None
                session._cached_fbprofile = None
        request.fbgraph = session._cached_fbgraph
        request.fbprofile = session._cached_fbprofile

        if not request.fbprofile:
             #response = HttpResponseRedirect(reverse("logout"))
             #response.delete_cookie(settings.FACEBOOK_API_KEY + '_user')
             #response.delete_cookie(settings.FACEBOOK_API_KEY + '_session_key')
             #response.delete_cookie(settings.FACEBOOK_API_KEY + '_expires')
             #response.delete_cookie(settings.FACEBOOK_API_KEY + '_ss')
             #response.delete_cookie(settings.FACEBOOK_API_KEY)
             #response.delete_cookie('fbsetting_' + settings.FACEBOOK_API_KEY)
             return None

        if request.path.find("admin") != -1: return None
        if (request.path.find(reverse('fbreg')) == -1) and (request.path.find(reverse('fblink')) == -1) and (request.path.find(reverse('terms')) == -1) and (request.path.find("/style/",0,7) == -1) and (request.path.find("/images/",0,8) == -1):
            fbuser = None
            try:
                fbuser = FBUser.objects.get(uid=cookie["uid"])
            except:
                url = reverse('fbreg')
                qs = '='.join(['next', quote(request.path)])
                fullurl = '?'.join((url,qs))

                return HttpResponseRedirect(fullurl)
            if fbuser.access_token != cookie["access_token"]:
                fbuser.access_token = cookie['access_token']
                fbuser.save()
            user = fbuser.authenticate()
            login(request, user)
        return None


        #try:
        #    request.fbgraph = facebook.GraphAPI(request.fbcookie["access_token"])
        #except:
        #    request.fbgraph = None
        #request.fbgraph = LazyFBGraph()
        #try:
        #    request.fbprofile = facebook.GraphAPI(request.fbcookie["access_token"]).get_object("me")
        #except:
        #    request.fbprofile = None
        #request.fbprofile = LazyFBProfile()
