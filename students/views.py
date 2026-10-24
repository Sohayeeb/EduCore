from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.http import HttpResponse
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
import csv

from .models import Student
from .serializers import StudentSerializer, StudentListSerializer


# ── API ViewSet ──────────────────────────────────────────────
class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['course', 'status']
    search_fields = ['name', 'email', 'phone']
    ordering_fields = ['name', 'enrolled_at', 'gpa']

    def get_serializer_class(self):
        if self.action == 'list':
            return StudentListSerializer
        return StudentSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        total = Student.objects.count()
        by_course = list(Student.objects.values('course').annotate(count=Count('id')))
        by_status = list(Student.objects.values('status').annotate(count=Count('id')))
        avg_gpa = Student.objects.aggregate(avg=Avg('gpa'))['avg']
        return Response({
            'total_students': total,
            'by_course': by_course,
            'by_status': by_status,
            'average_gpa': round(avg_gpa, 2) if avg_gpa else 0,
        })

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def export_csv(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="students.csv"'
        writer = csv.writer(response)
        writer.writerow(['ID', 'Name', 'Email', 'Phone', 'Course', 'Status', 'GPA', 'Enrolled At'])
        for s in Student.objects.all():
            writer.writerow([s.id, s.name, s.email, s.phone, s.course, s.status, s.gpa, s.enrolled_at])
        return response

    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        ids = request.data.get('ids', [])
        deleted, _ = Student.objects.filter(id__in=ids).delete()
        return Response({'message': f'{deleted} student(s) deleted'})


# ── Template Views ───────────────────────────────────────────
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, 'Invalid credentials')
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    query = request.GET.get('q', '')
    course_filter = request.GET.get('course', '')
    status_filter = request.GET.get('status', '')

    students = Student.objects.all()

    if query:
        students = students.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone__icontains=query)
        )
    if course_filter:
        students = students.filter(course=course_filter)
    if status_filter:
        students = students.filter(status=status_filter)

    total = Student.objects.count()
    active = Student.objects.filter(status='active').count()
    graduated = Student.objects.filter(status='graduated').count()
    avg_gpa = Student.objects.aggregate(avg=Avg('gpa'))['avg']
    by_course = Student.objects.values('course').annotate(count=Count('id'))

    return render(request, 'dashboard.html', {
        'students': students,
        'query': query,
        'course_filter': course_filter,
        'status_filter': status_filter,
        'total': total,
        'active': active,
        'graduated': graduated,
        'avg_gpa': round(avg_gpa, 2) if avg_gpa else 0,
        'by_course': list(by_course),
        'courses': Student.COURSE_CHOICES,
        'statuses': Student.STATUS_CHOICES,
    })


@login_required
def student_create(request):
    if request.method == 'POST':
        try:
            Student.objects.create(
                name=request.POST['name'],
                email=request.POST['email'],
                phone=request.POST['phone'],
                course=request.POST['course'],
                status=request.POST.get('status', 'active'),
                address=request.POST.get('address', ''),
                gpa=request.POST.get('gpa') or None,
                profile_picture=request.FILES.get('profile_picture'),
            )
            messages.success(request, 'Student added successfully')
            return redirect('dashboard')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    return render(request, 'student_form.html', {
        'courses': Student.COURSE_CHOICES,
        'statuses': Student.STATUS_CHOICES,
        'action': 'Add',
    })


@login_required
def student_update(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        try:
            student.name = request.POST['name']
            student.email = request.POST['email']
            student.phone = request.POST['phone']
            student.course = request.POST['course']
            student.status = request.POST.get('status', 'active')
            student.address = request.POST.get('address', '')
            student.gpa = request.POST.get('gpa') or None
            if request.FILES.get('profile_picture'):
                student.profile_picture = request.FILES['profile_picture']
            student.save()
            messages.success(request, 'Student updated successfully')
            return redirect('dashboard')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    return render(request, 'student_form.html', {
        'student': student,
        'courses': Student.COURSE_CHOICES,
        'statuses': Student.STATUS_CHOICES,
        'action': 'Update',
    })


@login_required
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.delete()
        messages.success(request, 'Student deleted')
        return redirect('dashboard')
    return render(request, 'student_confirm_delete.html', {'student': student})


@login_required
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    return render(request, 'student_detail.html', {'student': student})