from django.conf import settings
import facebook
from django.http import HttpResponseRedirect
from fbuser.models import FBUser
from django.core.urlresolvers import reverse
from django.contrib.auth import login, logout
from urllib import quote
import re
from fbuser.urls import urlpatterns as fb_urls
from django.contrib.auth.models import User
from fbuser.util import existing_fbuser, email_match, get_fb_cookie, same_auth

class LazyFBGraph(object):
    def __get__(self, request, obj_type=None):
        session = request.session
        if not session.get('fbgraph', None):
            try:
                session['fbgraph'] = facebook.GraphAPI(request.fbcookie["access_token"])
            except:
                return None
        return session.get('fbgraph', None)

class LazyFBProfile(object):
    def __get__(self, request, obj_type=None):
        session = request.session
        if not session.get('fbprofile', None):
            try:
                session['fbprofile'] = facebook.GraphAPI(request.fbcookie["access_token"]).get_object("me")
            except:
                return None
        return session.get('fbprofile', None)

class FBProfile:

    ignore = []

    def __init__(self):
        if len(FBProfile.ignore) == 0:
            for url in fb_urls:
                FBProfile.ignore.append(re.compile(reverse(url.name)))
            for path in settings.FACEBOOK_IGNORE_PATHS:
                FBProfile.ignore.append(re.compile(path))


    def process_request(self, request):
        # exempt certain paths from triggering the middleware.
        # example: css files, or terms and conditions.
        for path in FBProfile.ignore:
            if (path.match(request.path)):
                return None
        # The we try to turn the facebook cookie into a user.
        cookie = get_fb_cookie(request)
        # There is an error with the cookie, or the user isn't logged
        # in to facebook.
        if not cookie:
#            if request.user.is_authenticated():
#                try:
#                    # if user is logged in, and has an FBUser object,
#                    # log them out.
#                    #TODO: this seems wrong-ola; the user cannot login
#                    #TODO: with normal credentials if they are fb-enabled. meh.
#                    fbuser = FBUser.objects.get(user__username=request.user.username)
#                    logout(request)
#                except:
#                    pass
            return None
        else:
            pass
        request.fbcookie = cookie
        session = request.session
        if not session.get('fbprofile', None) or not same_auth(request, session):
            try:
                session['fbgraph'] = facebook.GraphAPI(request.fbcookie["access_token"])
                session['fbprofile'] = session['fbgraph'].get_object("me")
            except:
                session['fbgraph'] = None
                session['fbprofile'] = None
        request.fbgraph = session['fbgraph']
        request.fbprofile = session['fbprofile']

        if not (request.fbgraph and request.fbprofile):
            return None

        fbuser = existing_fbuser(cookie)

        # if match_fb_id(request):
        #     return HttpResponseRedirect(next)
        if fbuser:
            #TODO: Smoking crack?
            #TODO: The user is logged in, and logging in with
            #TODO: a Facebook account that is already connected.
            if request.user:
                logout(request)
            # TODO: We don't actually use this.  Remove?
            if fbuser.access_token != cookie["access_token"]:
                fbuser.access_token = cookie['access_token']
                fbuser.save()
            user = fbuser.authenticate()
            login(request, user)
            return None

        else:
            #TODO: this isn't a Facebook account we know about yet.
            #TODO: if this user is already logged in, should we just pop a simple, "are you sure you want to connect these"?
            if request.user or email_match(request):
                url = reverse('fblink')
            else:
                url = reverse('fbreg')
            qs = '='.join(['next', quote(request.path)])
            full_url = '?'.join((url,qs))

            return HttpResponseRedirect(full_url)


