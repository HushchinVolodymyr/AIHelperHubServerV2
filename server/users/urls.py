from django.urls import path

from .views import RegisterView, LoginView, LogoutView, UserView, GoogleLoginView

urlpatterns = [
    path("register", RegisterView.as_view(), name="register"),
    path("login", LoginView.as_view(), name="login"),
    path("logout", LogoutView.as_view(), name="logout"),
    path("user", UserView.as_view(), name="user"),
    path('auth/google/', GoogleLoginView.as_view(), name='google_login'),
]
