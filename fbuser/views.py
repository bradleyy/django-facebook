import facebook
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.core.urlresolvers import reverse
from fbuser.models import FBUser
from django.template import RequestContext
from django.http import HttpResponseRedirect
from fbuser.forms import *
from fbuser.util import get_next


def fbreg(request):
    next = get_next(request)
    fbprofile = request.session.get("fbprofile", None)
    fbgraph = request.session.get("fbgraph", None)
    if not (fbprofile and fbgraph):
        return HttpResponseRedirect('/')
    else:
        if match_fb_id(request):
            return HttpResponseRedirect(next)
    if request.method == "POST":
        user = User.objects.create_user(request.fbprofile['id'],
                                        '', password=None)
        user.first_name = fbprofile['first_name']
        user.last_name = fbprofile['last_name']
        user.email = fbprofile['email']
        user.is_active = True
        user.set_unusable_password()
        user.save()
        profile = user.get_profile()
        profile.active=True
        profile.save()
        fbuser = FBUser(
            user=user,
            uid=fbprofile['id'],
            name=fbprofile['name'],
            profile_url=fbprofile['link'],
            access_token=getattr(fbgraph,'access_token', None),
            )
        fbuser.save()
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
def fblink(request):
    next = get_next(request)
    fbprofile = request.session.get("fbprofile", None)
    fbgraph = request.session.get("fbgraph", None)
    if not (fbprofile and fbgraph):
        return HttpResponseRedirect('/')
    message = ""
    if request.method=="GET":
        form = AuthenticationForm()
    else:
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                if not hasattr(user, 'fb_set'):
                    if user.is_active:
                        login(request, user)
                        profile = user.get_profile()
                        profile.active=True
                        profile.save()
                        try:
                            #import rpdb2; rpdb2.start_embedded_debugger('a')
                            user_old = User.objects.get(id=fbprofile['id'])
                            fbuser = FBUser.objects.get(user=user_old)
                            fbuser.user = user
                            fbuser.save()
                            #TODO: delete user_old
                        except:
                            fbuser = FBUser(
                                user=user,
                                uid=fbprofile['id'],
                                name=fbprofile['name'],
                                profile_url=fbprofile['link'],
                                access_token=getattr(fbgraph,'access_token', None),
                                )
                            fbuser.save()
                        # Redirect to a success page.
                        return HttpResponseRedirect(next)
                    else:
                        # Return a 'disabled account' error message
                        pass
                else:
                    message = "This account already has a Facebook account associated with it."
            else:
                # Return an 'invalid login' error message.
                message = "Login invalid"
                pass
    return render_to_response('fbuser/signup.djhtml',
                              {'path': request.path,
                               'form': form,
                               'message': message,
                               },
                              context_instance=RequestContext(request)
                              )
