from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from functools import wraps

# def check_user(user):
#     return not user.is_authenticated

# user_logout_required = user_passes_test(check_user, 'logout', None)

# def deny_auth_user(view_func):
#     return user_logout_required(view_func)


# def deny_user(view_func):
#     @wraps(view_func)
#     def wrapper(request, *args, **kwargs):
#         if request.user.is_authenticated:
#             redirect('logout')
#         return view_func(request, *args, **kwargs)
#     return wrapper


# def student_only(view_func):
#     @wraps(view_func)
#     def wrapper(request, *args, **kwargs):
#         if not request.user.is_student:
#             redirect('logout')
#         return view_func(request, *args, **kwargs)
#     return wrapper

      
# def HOD_only(view_func):
#     @wraps(view_func)
#     def wrapper(request, *args, **kwargs):
#         if not request.user.is_hod:
#             redirect('logout')
#         return view_func(request, *args, **kwargs)
#     return wrapper



def deny_user(condition_func):
    """
    A combined decorator that applies a condition function to restrict access.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if condition_func(request):
                return redirect('logout')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def is_authenticated(request):
    return True if request.user.is_authenticated else False

def is_not_student(request):
    return True if not request.user.is_student else False

def is_not_hod(request):
    return True if not request.user.is_hod else False

