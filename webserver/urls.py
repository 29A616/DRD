from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('signin/', views.signin, name='signin'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('diagnostic/', views.diagnostic, name='diagnostic'),
    path('save-active-tab/', views.save_active_tab, name='save_active_tab'),
    path('get-patient-data/<int:patient_id>/',
         views.get_patient_data, name='get_patient_data'),
    path('set-selected-patient/', views.set_selected_patient,
         name='set_selected_patient'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
