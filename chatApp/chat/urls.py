from django.urls import path
from . import views
urlpatterns = [
    path('', views.login,name="login"),    
    path('logout', views.logout,name="logout"),    
    path('register', views.register,name="register"),    
    path('chat', views.messages_page,name="ChatHome"),    
]