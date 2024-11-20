
from django.urls import path

from contacts.views import ContactView

urlpatterns = [
    path('create', ContactView.as_view(), name='create'),

]
