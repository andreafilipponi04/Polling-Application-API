from django.urls import path
from .views import (
    RegisterAPIView,
    PollListCreateAPIView,
    PollRetrieveUpdateDestroyAPIView,
    VoteCreateAPIView,
    PollResultsAPIView,
    ChoiceCreateAPIView,
)

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('polls/', PollListCreateAPIView.as_view(), name='poll-list-create'),
    path('polls/<int:pk>/', PollRetrieveUpdateDestroyAPIView.as_view(), name='poll-detail'),
    path('polls/<int:pk>/results/', PollResultsAPIView.as_view(), name='poll-results'),
    path('votes/', VoteCreateAPIView.as_view(), name='vote-create'),
    path('choices/', ChoiceCreateAPIView.as_view(), name='choice-create'),
]