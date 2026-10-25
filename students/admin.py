from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_number', 'name', 'course', 'status', 'gpa', 'user']
    list_filter = ['course', 'status']
    search_fields = ['name', 'email', 'student_number']
