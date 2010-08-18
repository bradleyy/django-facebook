import facebook
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from fbuser.models import FBUser
from django.template import RequestContext
from django.http import HttpResponseRedirect
from fbuser.forms import *

# Create your views here.
def fbreg(request):
    if not hasattr(request, "fbprofile"):
        return HttpResponseRedirect('/')
    next = request.GET['next']
    if request.method == "POST":
        user = User.objects.create_user(request.fbprofile['id'],
                                        '', password=None)
        user.first_name = request.fbprofile['first_name']
        user.last_name = request.fbprofile['last_name']
        user.email = request.fbprofile['email']
        user.is_active = True
        user.set_unusable_password()
        user.save()
        profile = user.get_profile()
        profile.active=True
        profile.save()
        fbuser = FBUser(
            user=user,
            uid=request.fbprofile['id'],
            name=request.fbprofile['name'],
            profile_url=request.fbprofile['link'],
            access_token=request.fbcookie['access_token'],
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
    if not hasattr(request, "fbprofile"):
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
                            user_old = User.objects.get(id=request.fbprofile['id'])
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
                                uid=request.fbprofile['id'],
                                name=request.fbprofile['name'],
                                profile_url=request.fbprofile['link'],
                                access_token=request.fbcookie['access_token'],
                                )
                            fbuser.save()
                        # Redirect to a success page.
                        return HttpResponseRedirect(request.GET['next'])
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
