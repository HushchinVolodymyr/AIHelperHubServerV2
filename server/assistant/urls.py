from django.urls import path

from assistant.views import AssistantResponseView, AssistantCRUDView

urlpatterns = [
    path('response', AssistantResponseView.as_view(), name='assistant_response'),
    path('assistant_crud', AssistantCRUDView.as_view(), name='assistant_crud')
]