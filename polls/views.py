from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, filters
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import PollFilter
from .models import Poll, Vote, Choice
from .pagination import PollPagination
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (
    PollSerializer,
    VoteSerializer,
    PollResultSerializer,
    ChoiceSerializer,
    RegisterSerializer,
)


class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class PollListCreateAPIView(generics.ListCreateAPIView):
    queryset = Poll.objects.all().order_by('-created_at')
    serializer_class = PollSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = PollFilter
    ordering_fields = ['created_at', 'updated_at']
    search_fields = ['question', 'choices__text']
    pagination_class = PollPagination

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class PollRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrAdminOrReadOnly,
    ]


class VoteCreateAPIView(generics.CreateAPIView):
    queryset = Vote.objects.all().order_by('-voted_at')
    serializer_class = VoteSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PollResultsAPIView(APIView):
    permission_classes = [AllowAny]

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
                'percentage': f'{percentage:.2f}',
            })

        data = {
            'poll_id': poll.id,
            'question': poll.question,
            'total_votes': total_votes,
            'choices': choices_data,
        }

        serializer = PollResultSerializer(instance=data)
        return Response(serializer.data)


class ChoiceCreateAPIView(generics.CreateAPIView):
    queryset = Choice.objects.all()
    serializer_class = ChoiceSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        poll = serializer.validated_data['poll']

        if poll.created_by != self.request.user:
            raise PermissionDenied(
                "Puoi aggiungere scelte solo ai sondaggi che hai creato tu."
            )

        serializer.save()


class VotedPollsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        voted_poll_ids = Vote.objects.filter(
            user=request.user
        ).values_list('poll_id', flat=True).distinct()

        polls = Poll.objects.filter(id__in=voted_poll_ids)
        serializer = PollSerializer(polls, many=True)
        return Response(serializer.data)