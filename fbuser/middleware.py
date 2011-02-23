from django.conf import settings
import facebook
from django.http import HttpResponseRedirect
from fbuser.models import FBUser
from django.core.urlresolvers import reverse
from django.contrib.auth import login, logout
from urllib import quote
from fbuser.util import same_auth


class FBProfile:
    def process_request(self, request):
        user = facebook.get_user_from_cookie(
            request.COOKIES, settings.FACEBOOK_API_KEY,
            settings.FACEBOOK_SECRET_KEY)
        if not user:
            return None
        else:
            pass
        session = request.session
        session['fbuser'] = user
        if not session.get('fbprofile', None) or not same_auth(request, session):
            try:
                session['fbgraph'] = facebook.GraphAPI(session['fbuser']["access_token"])
                session['fbprofile'] = session['fbgraph'].get_object("me")
            except:
                session['fbgraph'] = None
                session['fbprofile'] = None
        request.fbgraph = session['fbgraph']
        request.fbprofile = session['fbprofile']

        if not (request.fbgraph and request.fbprofile):
            return None



