# from django.utils.timezone import datetime  # Para manejo de fechas
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserProfileForm, PatientForm, DiagnosticImageForm
from .models import Patient, DiagnosticImage
from diagnostic_tools.model_diagnostic import make_prediction, generate_gradcam
import os
from datetime import date


CLASS_MAPPING = {
    0: "No presenta retinopatía diabética",
    1: "Retinopatía diabética leve",
    2: "Retinopatía diabética moderada",
    3: "Retinopatía diabética severa",
    4: "Retinopatía diabética proliferativa"
}


def signin(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registro exitoso')
            return redirect('login')
    else:
        form = UserCreationForm()
        print(form)
    return render(request, 'webserver/signin.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'webserver/login.html', {'form': form})


@login_required
def user_logout(request):
    logout(request)
    return redirect('login')


def index(request):
    return render(request, 'webserver/index.html')


@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            if form.cleaned_data['password']:
                user.set_password(form.cleaned_data['password'])
            user.save()
            update_session_auth_hash(request, user)
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'webserver/profile.html', {'form': form})


@login_required
def diagnostic(request):
    patient_form = PatientForm()
    image_form = DiagnosticImageForm(user=request.user)
    patients = Patient.objects.filter(user=request.user).order_by('-id')
    diagnostics = None
    prediction_result = None
    selected_patient = None

    if request.method == 'POST':
        # Manejar registro de pacientes
        if 'register_patient' in request.POST:
            patient_form = PatientForm(request.POST)
            if patient_form.is_valid():
                patient = patient_form.save(commit=False)
                patient.user = request.user  # Asignar el usuario autenticado
                patient.save()
                messages.success(request, 'Paciente registrado exitosamente.')
                return redirect('/diagnostic/?tab=diagnostic-card')

        # Manejar edición de pacientes
        if 'update_patient' in request.POST:
            patient_id = request.POST.get('patient_id')
            patient = get_object_or_404(
                Patient, id=patient_id, user=request.user)
            patient_form = PatientForm(request.POST, instance=patient)
            if patient_form.is_valid():
                patient_form.save()
                messages.success(
                    request, 'Datos del paciente actualizados exitosamente.')
                return redirect('/diagnostic/?tab=diagnostic-card')

        # Manejar eliminación de pacientes
        if 'delete_patient' in request.POST:
            patient_id = request.POST.get('patient_id')
            patient = get_object_or_404(
                Patient, id=patient_id, user=request.user)
            patient.delete()
            messages.success(request, 'Paciente eliminado exitosamente.')
            return redirect('/diagnostic/?tab=diagnostic-card')

        # Manejar deselección de paciente}
        if 'clean_patient' in request.POST:
            selected_patient = None

        # Manejar carga de imágenes
        if 'upload_image' in request.POST:
            image_form = DiagnosticImageForm(
                request.POST, request.FILES, user=request.user)
            if image_form.is_valid():
                diagnostic_image = image_form.save(commit=False)
                diagnostic_image.save()  # Guarda para asegurar nombre y rutas

                image_path = diagnostic_image.image.path
                predicted_class = make_prediction(image_path)
                diagnosis_text = CLASS_MAPPING.get(
                    predicted_class, "Error en la clasificación")

                # Asignar el resultado del diagnóstico
                diagnostic_image.diagnosis_result = diagnosis_text
                diagnostic_image.save()  # Guarda el resultado del diagnóstico

                # Generar Grad-CAM
                gradcam_path = os.path.join(
                    'media', diagnostic_image.gradcam_image.name)
                try:
                    generate_gradcam(image_path, gradcam_path)
                except Exception as e:
                    messages.error(request, f"Error al generar Grad-CAM: {e}")

                # Actualizar prediction_result para mostrarlo en la tarjeta de diagnóstico
                prediction_result = diagnosis_text

                return redirect('/diagnostic/?tab=diagnostic-card')

    elif request.method == 'GET' and 'patient_id' in request.GET:
        patient_id = request.GET.get('patient_id')
        selected_patient = get_object_or_404(
            Patient, id=patient_id, user=request.user)
        patient_form = PatientForm(instance=selected_patient)

    # Método para filtrar por fecha y nombre de paciente
    if request.method == 'GET':
        date_filter = request.GET.get('date_filter', str(date.today()))
        patient_name_filter = request.GET.get('patient_name_filter', '')

        diagnostics = DiagnosticImage.objects.filter(
            patient__user=request.user
        )

        # Filtrar por fecha si el filtro de fecha fue proporcionado
        if date_filter:
            diagnostics = diagnostics.filter(
                consultation_date__date=date_filter)

        # Ordenar por fecha de consulta en orden descendente
        diagnostics = diagnostics.order_by('-consultation_date')

    return render(request, 'webserver/diagnostic.html', {
        'patient_form': patient_form,
        'image_form': image_form,
        'patients': patients,
        'diagnostics': diagnostics,
        'prediction_result': prediction_result,
        'selected_patient': selected_patient,
        'today': date.today()
    })
