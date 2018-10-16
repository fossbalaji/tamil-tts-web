"""tamil_tts_web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from ttsapp.views import SignupPageView, LoginPageView, AboutPageView, HomePageView, LogoutView, Fileupload, \
    PreferenceView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomePageView.as_view(), name='home'),
    path('signup/', SignupPageView.as_view(), name='signup'),
    path('login/', LoginPageView.as_view(), name='login'),
    path('about/', AboutPageView.as_view(), name='about'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('upload/', Fileupload.as_view(), name='upload'),
    path('preferences/', PreferenceView.as_view(), name='preferences'),
]
