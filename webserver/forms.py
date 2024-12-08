from .models import Patient
from django import forms
from django.contrib.auth.models import User
from .models import Patient, DiagnosticImage


class UserProfileForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'readonly': 'readonly'}),
        }

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password:
            return self.instance.password
        return password


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['first_name', 'last_name',
                  'age', 'medical_history', 'contact']


class DiagnosticImageForm(forms.ModelForm):
    class Meta:
        model = DiagnosticImage
        fields = ['patient', 'image']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['patient'].queryset = Patient.objects.filter(
                user=user)  # Filtra pacientes por usuario
        self.fields['patient'].empty_label = "Seleccione un paciente"
