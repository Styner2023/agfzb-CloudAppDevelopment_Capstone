"""
This module defines the URL patterns for the djangoapp application.
"""
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from djangoapp import views

app_name = 'djangoapp'
urlpatterns = [
    path('admin/', admin.site.urls),
    path('djangoapp/', views.get_dealerships, name='djangoapp1'),
    path('dealerships/', views.list_dealerships, name='dealerships'),
    path('', views.get_dealerships, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('dealer/<int:dealer_id>/', views.get_dealer_by_id, name='dealer_details'),
    path('dealer/<int:dealer_id>/add-review/', views.add_review, name="add_review"),
    path('dealership/<int:dealer_id>/', views.view_dealership, name='view_dealership'),
    path('login/', views.login_view, name='login'),  # login_view is the view function for login
    path('logout/', LogoutView.as_view(), name='logout'),
    path('some_path/', views.some_function, name='some_function'),
    path('register/', views.register, name='register'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# https://kstiner101-8000.theiadockernext-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/djangoapp/
# https://kstiner101-3000.theiadockernext-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get
