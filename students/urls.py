from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'students', views.StudentViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/auth/', include('rest_framework.urls')),

    # Auth
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_choice, name='signup'),
    path('signup/admin/', views.signup_admin, name='signup-admin'),
    path('signup/student/', views.signup_student, name='signup-student'),
    path('signup/pending/', views.signup_pending, name='signup-pending'),

    # Student CRUD (admin)
    path('students/create/', views.student_create, name='student-create'),
    path('students/<int:pk>/', views.student_detail, name='student-detail'),
    path('students/<int:pk>/update/', views.student_update, name='student-update'),
    path('students/<int:pk>/delete/', views.student_delete, name='student-delete'),

    # Assignments
    path('assignments/create/', views.assignment_create, name='assignment-create'),
    path('assignments/<int:pk>/delete/', views.assignment_delete, name='assignment-delete'),


    # Allowed IDs
    path('allowed-ids/', views.allowed_ids, name='allowed-ids'),

    
    # Messaging
    path('inbox/', views.inbox, name='inbox'),
    path('inbox/<int:user_id>/', views.conversation_view, name='conversation'),
    path('groups/', views.group_list, name='group-list'),
    path('groups/<int:group_id>/', views.group_view, name='group-view'),
]
