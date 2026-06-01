from django.urls import path
from .views import (
    PollListCreateAPIView,
    PollRetrieveUpdateDestroyAPIView,
    VoteCreateAPIView,
    PollResultsAPIView,
)

urlpatterns = [
    path('polls/', PollListCreateAPIView.as_view(), name='poll-list-create'),
    path('polls/<int:pk>/', PollRetrieveUpdateDestroyAPIView.as_view(), name='poll-detail'),
    path('polls/<int:pk>/results/', PollResultsAPIView.as_view(), name='poll-results'),
    path('votes/', VoteCreateAPIView.as_view(), name='vote-list-create'),
]