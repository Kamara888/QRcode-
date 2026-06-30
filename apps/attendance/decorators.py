from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone


def sudo_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        verified = request.session.get('sudo_verified')
        if not verified:
            request.session['sudo_redirect'] = request.path
            return redirect('sudo-confirm')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
