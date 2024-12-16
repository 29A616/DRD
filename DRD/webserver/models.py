import os
import uuid
from django.db import models
from django.contrib.auth.models import User


def diagnostic_images_upload_to(instance, filename):
    # Genera un nombre único con UUID para la imagen al momento de asignarla.
    ext = os.path.splitext(filename)[1]
    unique_name = f"{uuid.uuid4()}{ext}"
    return f"diagnostic_images/{unique_name}"


class Patient(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.IntegerField()
    medical_history = models.TextField()
    contact = models.CharField(max_length=100)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="patients")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class DiagnosticImage(models.Model):
    id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(
        'Patient', on_delete=models.CASCADE, related_name='diagnostic_images')
    image = models.ImageField(upload_to=diagnostic_images_upload_to)
    gradcam_image = models.ImageField(
        upload_to=diagnostic_images_upload_to, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    diagnosis_result = models.TextField(blank=True, null=True)
    consultation_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        creating = self.pk is None
        # Primero guarda para que image obtenga su nombre final
        super().save(*args, **kwargs)

        # Si es la primera vez que se guarda y aún no hay gradcam, la creamos
        if creating and self.image and not self.gradcam_image:
            base_name = os.path.splitext(os.path.basename(self.image.name))[0]
            gc_name = f"{base_name}-gc.png"
            # Asigna el nombre sin volver a aplicar upload_to, ya que el archivo gradcam se generará manualmente.
            self.gradcam_image.name = f"diagnostic_images/{gc_name}"
            super().save(*args, **kwargs)
