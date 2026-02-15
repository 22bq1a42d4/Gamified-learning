# accounts/decorators.py

from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from functools import wraps

def role_required(required_role):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.role != required_role:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
