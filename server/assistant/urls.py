from django.urls import path

from assistant.views import AssistantResponseView, AssistantCRUDView, Assistants, UserAssistantResponse

urlpatterns = [
    path('response', AssistantResponseView.as_view(), name='assistant_response'),
    path('user_assistant_response', UserAssistantResponse.as_view(), name='user_assistant_response'),

    path('crud', AssistantCRUDView.as_view(), name='assistant_crud'),
    path('crud/<int:assistant_id>', AssistantCRUDView.as_view(), name='assistant_get'),

    path('list', Assistants.as_view(), name='assistant_list'),
]

