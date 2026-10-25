from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Student


class AdminSignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-input'
            field.widget.attrs['autocomplete'] = 'off'
        self.fields['username'].widget.attrs['placeholder'] = 'Enter username'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter email'
        self.fields['password1'].widget.attrs['placeholder'] = 'Enter password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm password'

    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.is_active = False
        if commit:
            user.save()
        return user


class StudentSignUpForm(UserCreationForm):
    student_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your student number',
            'autocomplete': 'off',
        })
    )
    course = forms.ChoiceField(
        choices=Student.COURSE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter phone number',
            'autocomplete': 'off',
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if not hasattr(field.widget, 'attrs'):
                continue
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-input'
            field.widget.attrs['autocomplete'] = 'off'
        self.fields['username'].widget.attrs['placeholder'] = 'Choose a username'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter email'
        self.fields['password1'].widget.attrs['placeholder'] = 'Enter password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm password'

    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def clean_student_number(self):
        from .models import AllowedStudentID
        sn = self.cleaned_data['student_number'].strip()
        if not AllowedStudentID.objects.filter(student_number=sn).exists():
            raise forms.ValidationError('This student number is not on the allowed list.')
        if Student.objects.filter(student_number=sn).exists():
            raise forms.ValidationError('This student number is already registered.')
        return sn

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.is_active = True
        if commit:
            user.save()
            Student.objects.create(
                user=user,
                student_number=self.cleaned_data['student_number'],
                name=user.username,
                email=user.email,
                phone=self.cleaned_data['phone'],
                course=self.cleaned_data['course'],
            )
        return user


class StudentModelForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['student_number', 'name', 'email', 'phone', 'course', 'status', 'address', 'gpa', 'profile_picture']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-input'
        self.fields['address'].widget.attrs['rows'] = 3
        self.fields['student_number'].widget.attrs['placeholder'] = 'e.g. STU-2024-001'