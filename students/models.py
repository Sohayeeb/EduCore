from django.db import models
from django.contrib.auth.models import User


class Student(models.Model):
    COURSE_CHOICES = [
        ('Python', 'Python'),
        ('Django', 'Django'),
        ('Java', 'Java'),
        ('Web Development', 'Web Development'),
        ('Data Science', 'Data Science'),
        ('Machine Learning', 'Machine Learning'),
        ('Cybersecurity', 'Cybersecurity'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('graduated', 'Graduated'),
        ('suspended', 'Suspended'),
    ]

    # Linked Django user account (set when student signs up)
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='student_profile'
    )

    student_number = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    course = models.CharField(max_length=50, choices=COURSE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    gpa = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    enrolled_at = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.student_number})"

    class Meta:
        ordering = ['-enrolled_at']

class AllowedStudentID(models.Model):
    student_number = models.CharField(max_length=20, unique=True)
    note = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.student_number

    class Meta:
        ordering = ['student_number']
