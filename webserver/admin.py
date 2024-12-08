from django.contrib import admin
from .models import Patient, DiagnosticImage


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'age',
                    'user')  # Campos visibles en la lista
    search_fields = ('first_name', 'last_name',
                     'user__username')  # Campos para buscar
    list_filter = ('user',)  # Filtros en la barra lateral
    ordering = ('last_name',)  # Orden por defecto


@admin.register(DiagnosticImage)
class DiagnosticImageAdmin(admin.ModelAdmin):
    # Asegúrate de incluir 'patient'
    list_display = ('id', 'patient', 'uploaded_at', 'diagnosis_result')
    # Los campos aquí deben estar en list_display
    list_display_links = ('id', 'patient')
    search_fields = ('patient__first_name', 'patient__last_name',
                     'diagnosis_result')  # Campos para buscar
    # Filtros en la barra lateral
    list_filter = ('consultation_date', 'patient__user')
    ordering = ('-uploaded_at',)  # Orden por defecto
