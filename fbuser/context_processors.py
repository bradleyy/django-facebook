from django.conf import settings

def FacebookApiKey(request):
    if hasattr(settings, "FACEBOOK_API_KEY"):
        return {'facebook_api_key': settings.FACEBOOK_API_KEY}
    else:
        return {}

def FacebookProfile(request):
    fbprofile = request.session.get("fbprofile", None)
    if fbprofile:
        return {'facebook_profile': fbprofile }
    else:
        return {}
