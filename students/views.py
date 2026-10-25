from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.http import HttpResponse
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
import csv

from .models import Student
from .serializers import StudentSerializer, StudentListSerializer
from .forms import AdminSignUpForm, StudentSignUpForm, StudentModelForm
from messaging.models import Assignment, Conversation, Message, Group


# ── Helpers ──────────────────────────────────────────────────

def is_admin_user(user):
    return user.is_authenticated and not hasattr(user, 'student_profile')


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

    @action(detail=False, methods=['get'],
            authentication_classes=[SessionAuthentication],
            permission_classes=[IsAuthenticated])
    def export_csv(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="students.csv"'
        writer = csv.writer(response)
        writer.writerow(['ID', 'Student Number', 'Name', 'Email', 'Phone', 'Course', 'Status', 'GPA', 'Enrolled At'])
        for s in Student.objects.all():
            writer.writerow([s.id, s.student_number, s.name, s.email, s.phone, s.course, s.status, s.gpa, s.enrolled_at])
        return response

    @action(detail=False, methods=['post'],
            authentication_classes=[SessionAuthentication],
            permission_classes=[IsAuthenticated])
    def bulk_delete(self, request):
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'message': 'No students selected'}, status=400)
        deleted, _ = Student.objects.filter(id__in=ids).delete()
        return Response({'message': f'{deleted} student(s) deleted'})


# ── Authentication Views ─────────────────────────────────────

def signup_choice(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'signup_choice.html')


def signup_admin(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = AdminSignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('signup-pending')
    else:
        form = AdminSignUpForm()
    return render(request, 'signup_admin.html', {'form': form})


def signup_student(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = StudentSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = StudentSignUpForm()
    return render(request, 'signup_student.html', {'form': form})


def signup_pending(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'signup_pending.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        try:
            pending_user = User.objects.get(username=username)
            if not pending_user.is_active:
                messages.error(request, 'Your account is waiting for admin approval.')
            else:
                messages.error(request, 'Invalid credentials')
        except User.DoesNotExist:
            messages.error(request, 'Invalid credentials')
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


# ── Dashboard ────────────────────────────────────────────────

@login_required
def dashboard(request):
    try:
        if request.user.student_profile:
            return student_dashboard(request)
    except Exception:
        pass
    return admin_dashboard(request)


# ── Admin Dashboard ──────────────────────────────────────────

@login_required
def admin_dashboard(request):
    query = request.GET.get('q', '')
    course_filter = request.GET.get('course', '')
    status_filter = request.GET.get('status', '')

    students = Student.objects.all()
    if query:
        students = students.filter(
            Q(name__icontains=query) | Q(email__icontains=query) | Q(phone__icontains=query)
        )
    if course_filter:
        students = students.filter(course=course_filter)
    if status_filter:
        students = students.filter(status=status_filter)

    total = Student.objects.count()
    active = Student.objects.filter(status='active').count()
    graduated = Student.objects.filter(status='graduated').count()
    avg_gpa = Student.objects.aggregate(avg=Avg('gpa'))['avg']
    by_course = list(Student.objects.values('course').annotate(count=Count('id')))
    by_status = list(Student.objects.values('status').annotate(count=Count('id')))
    assignments = Assignment.objects.order_by('due_date')[:5]
    pending_users = User.objects.filter(is_active=False)

    return render(request, 'dashboard_admin.html', {
        'students': students,
        'query': query,
        'course_filter': course_filter,
        'status_filter': status_filter,
        'total': total,
        'active': active,
        'graduated': graduated,
        'avg_gpa': round(avg_gpa, 2) if avg_gpa else 0,
        'by_course': by_course,
        'by_status': by_status,
        'courses': Student.COURSE_CHOICES,
        'statuses': Student.STATUS_CHOICES,
        'assignments': assignments,
        'pending_users': pending_users,
    })


# ── Student Dashboard ────────────────────────────────────────

@login_required
def student_dashboard(request):
    student = get_object_or_404(Student, user=request.user)
    assignments = Assignment.objects.filter(
        Q(course=student.course) | Q(course='')
    ).order_by('due_date')

    unread_dm = Message.objects.filter(
        conversation__participants=request.user,
        is_read=False
    ).exclude(sender=request.user).count()

    unread_group = Message.objects.filter(
        group__members=request.user,
        is_read=False
    ).exclude(sender=request.user).count()

    return render(request, 'dashboard_student.html', {
        'student': student,
        'assignments': assignments,
        'unread_dm': unread_dm,
        'unread_group': unread_group,
    })


# ── Student CRUD ─────────────────────────────────────────────

@login_required
def student_create(request):
    try:
        if request.user.student_profile:
            return redirect('dashboard')
    except Exception:
        pass
    if request.method == 'POST':
        form = StudentModelForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student added successfully')
            return redirect('dashboard')
    else:
        form = StudentModelForm()
    return render(request, 'student_form.html', {'form': form, 'action': 'Add'})


@login_required
def student_update(request, pk):
    try:
        if request.user.student_profile:
            return redirect('dashboard')
    except Exception:
        pass
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = StudentModelForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student updated successfully')
            return redirect('dashboard')
    else:
        form = StudentModelForm(instance=student)
    return render(request, 'student_form.html', {'form': form, 'action': 'Update', 'student': student})


@login_required
def student_delete(request, pk):
    try:
        if request.user.student_profile:
            return redirect('dashboard')
    except Exception:
        pass
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.delete()
        messages.success(request, 'Student deleted')
        return redirect('dashboard')
    return render(request, 'student_confirm_delete.html', {'student': student})


@login_required
def student_detail(request, pk):
    try:
        if request.user.student_profile:
            return redirect('dashboard')
    except Exception:
        pass
    student = get_object_or_404(Student, pk=pk)
    return render(request, 'student_detail.html', {'student': student})


# ── Assignments ──────────────────────────────────────────────

@login_required
def assignment_create(request):
    try:
        if request.user.student_profile:
            return redirect('dashboard')
    except Exception:
        pass
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        due_date = request.POST.get('due_date', '')
        course = request.POST.get('course', '')
        if title and description and due_date:
            Assignment.objects.create(
                title=title,
                description=description,
                due_date=due_date,
                course=course,
                created_by=request.user,
            )
            messages.success(request, 'Assignment posted')
            return redirect('dashboard')
        messages.error(request, 'Please fill in all required fields')
    return render(request, 'assignment_form.html', {'courses': Student.COURSE_CHOICES})


@login_required
def assignment_delete(request, pk):
    try:
        if request.user.student_profile:
            return redirect('dashboard')
    except Exception:
        pass
    assignment = get_object_or_404(Assignment, pk=pk)
    assignment.delete()
    messages.success(request, 'Assignment deleted')
    return redirect('dashboard')


# ── Messaging ────────────────────────────────────────────────

@login_required
def inbox(request):
    conversations = Conversation.objects.filter(
        participants=request.user
    ).prefetch_related('participants', 'messages').order_by('-created_at')

    groups = Group.objects.filter(members=request.user)

    user_list = []
    for u in User.objects.exclude(id=request.user.id).filter(is_active=True):
        try:
            role = f"Student · {u.student_profile.course}"
        except Exception:
            role = "Admin"
        user_list.append({'user': u, 'role': role})

    unread_dm = Message.objects.filter(
        conversation__participants=request.user,
        is_read=False
    ).exclude(sender=request.user).count()

    unread_group = Message.objects.filter(
        group__members=request.user,
        is_read=False
    ).exclude(sender=request.user).count()

    return render(request, 'inbox.html', {
        'conversations': conversations,
        'groups': groups,
        'user_list': user_list,
        'unread_dm': unread_dm,
        'unread_group': unread_group,
    })


@login_required
def conversation_view(request, user_id):
    other = get_object_or_404(User, pk=user_id)

    conv = Conversation.objects.filter(participants=request.user).filter(participants=other).first()
    if not conv:
        conv = Conversation.objects.create()
        conv.participants.add(request.user, other)

    if request.method == 'POST':
        body = request.POST.get('body', '').strip()
        if body:
            Message.objects.create(sender=request.user, conversation=conv, body=body)
        return redirect('conversation', user_id=user_id)

    conv.messages.exclude(sender=request.user).update(is_read=True)
    msgs = conv.messages.all()

    return render(request, 'conversation.html', {
        'other': other,
        'conversation': conv,
        'messages': msgs,
    })


@login_required
def group_list(request):
    if request.method == 'POST':
        try:
            if request.user.student_profile:
                return redirect('inbox')
        except Exception:
            pass
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        member_ids = request.POST.getlist('members')
        if name:
            group = Group.objects.create(name=name, description=description, created_by=request.user)
            group.members.add(request.user)
            for uid in member_ids:
                try:
                    group.members.add(User.objects.get(pk=uid))
                except User.DoesNotExist:
                    pass
            messages.success(request, f'Group "{name}" created')
        return redirect('inbox')
    return redirect('inbox')


@login_required
def group_view(request, group_id):
    group = get_object_or_404(Group, pk=group_id, members=request.user)

    if request.method == 'POST':
        body = request.POST.get('body', '').strip()
        if body:
            Message.objects.create(sender=request.user, group=group, body=body)
        return redirect('group-view', group_id=group_id)

    group.messages.exclude(sender=request.user).update(is_read=True)
    msgs = group.messages.all()

    return render(request, 'group_view.html', {
        'group': group,
        'messages': msgs,
    })


# ── Allowed IDs ──────────────────────────────────────────────

@login_required
def allowed_ids(request):
    try:
        if request.user.student_profile:
            return redirect('dashboard')
    except Exception:
        pass
    from .models import AllowedStudentID
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            sn = request.POST.get('student_number', '').strip()
            note = request.POST.get('note', '').strip()
            if sn:
                AllowedStudentID.objects.get_or_create(student_number=sn, defaults={'note': note})
                messages.success(request, f'{sn} added to allowed list')
        elif action == 'delete':
            pk = request.POST.get('pk')
            AllowedStudentID.objects.filter(pk=pk).delete()
            messages.success(request, 'ID removed')
        return redirect('allowed-ids')
    ids = AllowedStudentID.objects.all()
    return render(request, 'allowed_ids.html', {'ids': ids})