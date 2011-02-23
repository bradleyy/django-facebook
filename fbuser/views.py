from urllib import quote
from django.contrib.auth.views import logout
from django.core.urlresolvers import reverse
import facebook
from django.shortcuts import render_to_response, redirect
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from fbuser.models import FBUser
from django.template import RequestContext
from django.http import HttpResponseRedirect
from fbuser.forms import *
from fbuser.util import get_next


# Create your views here.
from fbuser.util import existing_fbuser, email_match
import settings

def fbreg(request, show_form=True):
    next = get_next(request)
    fbprofile = request.session.get("fbprofile", None)
    fbgraph = request.session.get("fbgraph", None)
    if not (fbprofile and fbgraph):
        return HttpResponseRedirect('/')
    next = request.GET.get('next', None)
    if request.method == "POST" or show_form==False:
        user = User.objects.create_user(request.fbprofile['id'],
                                        '', password=None)
        user.first_name = fbprofile['first_name']
        user.last_name = fbprofile['last_name']
        user.email = fbprofile['email']
        user.is_active = True
        user.set_unusable_password()
        user.save()
        fbuser = FBUser(
            user=user,
            uid=fbprofile['id'],
            name=fbprofile['name'],
            profile_url=fbprofile['link'],
            access_token=request.session['fbuser']["access_token"],
            )
        fbuser.save()
        user = fbuser.authenticate()
        login(request, user)
        facebook_new_account.send(sender=self, fbuser=fbuser, user=user)
        return HttpResponseRedirect(next)
    return render_to_response('fbuser/signup.djhtml',
                              {'path': request.path,
                               'form': None,
                               'next': next,
                               'show_terms': True,
                               'show_fblink': True,
                               },
                              context_instance=RequestContext(request)
                              )
def link_fb_user(request, user, fbprofile):
    if not hasattr(user, 'fb_set'):
        if user.is_active:
            login(request, user)
            #TODO: set callback to perform other user activation
            try:
                user_old = User.objects.get(id=fbprofile['id'])
                fbuser = FBUser.objects.get(user=user_old)
                for item in user_old.item_set:
                    item.owner = user
                    item.save()
                fbuser.user = user
                fbuser.save()
                #TODO: delete user_old
            except:
                fbuser = FBUser(
                    user=user,
                    uid=fbprofile['id'],
                    name=fbprofile['name'],
                    profile_url=fbprofile['link'],
                    access_token=request.session['fbuser']["access_token"],
                    )
                fbuser.save()
            user = fbuser.authenticate()
            login(request, user)
            # Redirect to a success page.
            facebook_link.send(sender=self, fbuser=fbuser, user=user)
            return HttpResponseRedirect(get_next(request)), user, ""
        else:
            # Return a 'disabled account' error message
            pass
    else:
        message = "This account already has a Facebook account associated with it."
        return None, None, ""

def fblink(request):
    next = get_next(request)
    fbprofile = request.session.get("fbprofile", None)
    fbgraph = request.session.get("fbgraph", None)
    if not (fbprofile and fbgraph):
        return HttpResponseRedirect('/')
    message = ""
    if request.method=="GET":
        try:
            from lazysignup.models import LazyUser
            from lazysignup.utils import is_lazy_user
            if is_lazy_user(request.user):
                redirect, user, message = link_fb_user(request, request.user, fbprofile)
                if redirect:
                    LazyUser.objects.filter(user=user).delete()
                    return redirect
                else:
                    pass
        except:
            pass
        form = AuthenticationForm()
    else:
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'],
                                password=form.cleaned_data['password'])
            if user is not None:
                redirect, user, message = link_fb_user(request, user, fbprofile)
                if redirect:
                    return redirect
                else:
                    pass
            else:
                # Return an 'invalid login' error message.
                message = "Login invalid"
                pass
        else:
            pass
    return render_to_response('fbuser/signup.djhtml',
                              {'path': request.path,
                               'form': form,
                               'message': message,
                               },
                              context_instance=RequestContext(request)
                              )
def fblogin(request):

    next = get_next(request)
    cookie_user = request.session.get('fbuser', None)
    if cookie_user:
        fbuser = existing_fbuser(cookie_user)
    else:
        fbuser = None

    # if match_fb_id(request):
    #     return HttpResponseRedirect(next)
    if fbuser:
        #TODO: Smoking crack?
        #TODO: The user is logged in, and logging in with
        #TODO: a Facebook account that is already connected.
        if request.user:
            pass
            #logout(request)
        # TODO: We don't actually use this.  Remove?
        if fbuser.access_token != cookie_user["access_token"]:
            fbuser.access_token = cookie_user['access_token']
            fbuser.save()
        user = fbuser.authenticate()
        login(request, user)
        return redirect(next)

    else:
        #TODO: this isn't a Facebook account we know about yet.
        #TODO: if this user is already logged in, should we just pop a simple, "are you sure you want to connect these"?
        if request.user.is_authenticated() or email_match(request):
            url = reverse('fblink')
        else:
            url = reverse('fbreg')
        qs = '='.join(['next', next])
        full_url = '?'.join((url,qs))

        return HttpResponseRedirect(full_url)

