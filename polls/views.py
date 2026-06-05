from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Poll, Vote
from .serializers import PollSerializer, VoteSerializer, PollResultSerializer
from .permissions import IsAuthorOrAdminOrReadOnly
from .filters import PollFilter
from .pagination import PollPagination


class PollListCreateAPIView(generics.ListCreateAPIView):
    queryset = Poll.objects.all().order_by('-created_at')
    serializer_class = PollSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = PollFilter
    search_fields = ['question']
    ordering_fields = ['created_at', 'updated_at']
    pagination_class = PollPagination

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class PollRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrAdminOrReadOnly]


class VoteCreateAPIView(generics.CreateAPIView):
    queryset = Vote.objects.all().order_by('-voted_at')
    serializer_class = VoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PollResultsAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        poll = get_object_or_404(Poll, pk=pk)

        total_votes = poll.votes.count()
        choices_data = []

        for choice in poll.choices.all():
            votes_count = choice.votes.count()
            percentage = (votes_count / total_votes * 100) if total_votes > 0 else 0

            choices_data.append({
                'id': choice.id,
                'text': choice.text,
                'votes_count': votes_count,
                'percentage': round(percentage, 2),
            })

        data = {
            'poll_id': poll.id,
            'question': poll.question,
            'total_votes': total_votes,
            'choices': choices_data,
        }

        serializer = PollResultSerializer(instance=data)
        return Response(serializer.data)