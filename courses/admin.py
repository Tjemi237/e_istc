from django.contrib import admin
from .models import Course, Module, Ressource

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'teacher', 'created_at')
    search_fields = ('title', 'teacher__username')

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    list_filter = ('course',)
    search_fields = ('title',)

@admin.register(Ressource)
class RessourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'module')
    list_filter = ('module__course', 'module')
    search_fields = ('title',)