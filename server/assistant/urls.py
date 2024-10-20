from django.urls import path

from assistant.views import AssistantResponseView, AssistantCRUDView

urlpatterns = [
    path('response', AssistantResponseView.as_view(), name='assistant_response'),
    path('crud', AssistantCRUDView.as_view(), name='assistant_crud'),
    path('crud/<int:assistant_id>', AssistantCRUDView.as_view(), name='assistant_get')
]

