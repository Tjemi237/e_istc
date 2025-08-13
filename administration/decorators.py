from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from users.models import User
from courses.models import Course, Module, Ressource, Annonce

def admin_required(function=None, login_url='users:login'):
    """
    Decorator for views that checks that the user is logged in and is an admin.
    If user is authenticated but not admin, raises PermissionDenied (403).
    If user is not authenticated, redirects to login_url.
    """
    def check_func(user):
        if not user.is_authenticated:
            return False # Will redirect to login_url
        if user.role == User.Role.ADMIN:
            return True
        raise PermissionDenied # Authenticated but not admin, raise 403

    actual_decorator = user_passes_test(
        check_func,
        login_url=login_url
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def course_owner_or_admin_required(function=None, login_url='users:login'):
    """
    Decorator for views that checks that the user is logged in and is either an admin
    or the teacher of the course.
    """
    def check_func(user, course_id):
        if not user.is_authenticated:
            return False
        if user.role == User.Role.ADMIN:
            return True
        try:
            course = Course.objects.get(pk=course_id)
            return course.teacher == user
        except Course.DoesNotExist:
            return False

    def actual_decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not check_func(request.user, kwargs['course_id']):
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return wrapper
    
    if function:
        return actual_decorator(function)
    return actual_decorator

def module_owner_or_admin_required(function=None, login_url='users:login'):
    """
    Decorator for views that checks that the user is logged in and is either an admin
    or the teacher of the module's course.
    """
    def check_func(user, module_id=None, course_id=None):
        if not user.is_authenticated:
            return False
        if user.role == User.Role.ADMIN:
            return True
        try:
            if module_id:
                module = Module.objects.get(pk=module_id)
                return module.course.teacher == user
            elif course_id:
                course = Course.objects.get(pk=course_id)
                return course.teacher == user
            return False
        except (Module.DoesNotExist, Course.DoesNotExist):
            return False

    def actual_decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not check_func(request.user, module_id=kwargs.get('module_id'), course_id=kwargs.get('course_id')):
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return wrapper
    
    if function:
        return actual_decorator(function)
    return actual_decorator

def ressource_owner_or_admin_required(function=None, login_url='users:login'):
    """
    Decorator for views that checks that the user is logged in and is either an admin
    or the teacher of the ressource's module's course.
    """
    def check_func(user, ressource_id=None, module_id=None):
        if not user.is_authenticated:
            return False
        if user.role == User.Role.ADMIN:
            return True
        try:
            if ressource_id:
                ressource = Ressource.objects.get(pk=ressource_id)
                return ressource.module.course.teacher == user
            elif module_id:
                module = Module.objects.get(pk=module_id)
                return module.course.teacher == user
            return False
        except (Ressource.DoesNotExist, Module.DoesNotExist):
            return False

    def actual_decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not check_func(request.user, ressource_id=kwargs.get('ressource_id'), module_id=kwargs.get('module_id')):
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return wrapper
    
    if function:
        return actual_decorator(function)
    return actual_decorator

def annonce_owner_or_admin_required(function=None, login_url='users:login'):
    """
    Decorator for views that checks that the user is logged in and is either an admin
    or the teacher of the annonce's course.
    """
    def check_func(user, annonce_id):
        if not user.is_authenticated:
            return False
        if user.role == User.Role.ADMIN:
            return True
        try:
            annonce = Annonce.objects.get(pk=annonce_id)
            return annonce.cours.teacher == user
        except Annonce.DoesNotExist:
            return False

    def actual_decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not check_func(request.user, kwargs['annonce_id']):
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return wrapper
    
    if function:
        return actual_decorator(function)
    return actual_decorator
