import django.dispatch

facebook_link = django.dispatch.Signal(providing_args=["fbuser", "user"])
facebook_new_account = django.dispatch.Signal(providing_args=["fbuser", "user"])
