from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Poll, Choice, Vote


User = get_user_model()


class PollAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='[email protected]',
            password='testpass123'
        )

        self.other_user = User.objects.create_user(
            username='otheruser',
            email='[email protected]',
            password='testpass123'
        )

        self.poll = Poll.objects.create(
            question='Pizza o pasta?',
            created_by=self.user,
            is_active=True
        )

        self.choice1 = Choice.objects.create(
            poll=self.poll,
            text='Pizza'
        )

        self.choice2 = Choice.objects.create(
            poll=self.poll,
            text='Pasta'
        )

    def test_get_polls_allowed_for_anonymous(self):
        url = reverse('poll-list-create')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_poll_denied_for_anonymous(self):
        url = reverse('poll-list-create')
        data = {
            'question': 'Nuovo sondaggio anonimo',
            'is_active': True
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_poll_allowed_for_authenticated_user(self):
        self.client.force_authenticate(user=self.user)

        url = reverse('poll-list-create')
        data = {
            'question': 'Nuovo sondaggio autenticato',
            'is_active': True
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Poll.objects.count(), 2)
        self.assertEqual(Poll.objects.latest('id').created_by, self.user)

    def test_author_can_update_own_poll(self):
        self.client.force_authenticate(user=self.user)

        url = reverse('poll-detail', kwargs={'pk': self.poll.pk})
        data = {
            'question': 'Domanda modificata',
            'is_active': True
        }

        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.poll.refresh_from_db()
        self.assertEqual(self.poll.question, 'Domanda modificata')

    def test_other_user_cannot_update_poll(self):
        self.client.force_authenticate(user=self.other_user)

        url = reverse('poll-detail', kwargs={'pk': self.poll.pk})
        data = {
            'question': 'Tentativo modifica non autore',
            'is_active': True
        }

        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_user_can_vote_once(self):
        self.client.force_authenticate(user=self.other_user)

        url = reverse('vote-list-create')
        data = {
            'poll': self.poll.id,
            'choice': self.choice1.id
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Vote.objects.count(), 1)

    def test_same_user_cannot_vote_twice_on_same_poll(self):
        Vote.objects.create(
            poll=self.poll,
            choice=self.choice1,
            user=self.other_user
        )

        self.client.force_authenticate(user=self.other_user)

        url = reverse('vote-list-create')
        data = {
            'poll': self.poll.id,
            'choice': self.choice2.id
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Vote.objects.count(), 1)

    def test_choice_must_belong_to_selected_poll(self):
        other_poll = Poll.objects.create(
            question='Altro sondaggio',
            created_by=self.user,
            is_active=True
        )

        other_choice = Choice.objects.create(
            poll=other_poll,
            text='Altra scelta'
        )

        self.client.force_authenticate(user=self.other_user)

        url = reverse('vote-list-create')
        data = {
            'poll': self.poll.id,
            'choice': other_choice.id
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_anonymous_can_view_poll_results(self):
        url = reverse('poll-results', kwargs={'pk': self.poll.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_poll_results_return_total_votes(self):
        Vote.objects.create(
            poll=self.poll,
            choice=self.choice1,
            user=self.other_user
        )

        third_user = User.objects.create_user(
            username='thirduser',
            email='[email protected]',
            password='testpass123'
        )

        Vote.objects.create(
            poll=self.poll,
            choice=self.choice2,
            user=third_user
        )

        url = reverse('poll-results', kwargs={'pk': self.poll.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_votes'], 2)

    def test_poll_results_return_votes_per_choice(self):
        Vote.objects.create(
            poll=self.poll,
            choice=self.choice1,
            user=self.other_user
        )

        third_user = User.objects.create_user(
            username='thirduser2',
            email='[email protected]',
            password='testpass123'
        )

        Vote.objects.create(
            poll=self.poll,
            choice=self.choice1,
            user=third_user
        )

        url = reverse('poll-results', kwargs={'pk': self.poll.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['choices'][0]['votes_count'], 2)
        self.assertEqual(response.data['choices'][1]['votes_count'], 0)

    def test_poll_results_return_zero_percentages_when_no_votes(self):
        url = reverse('poll-results', kwargs={'pk': self.poll.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_votes'], 0)
        self.assertEqual(response.data['choices'][0]['percentage'], '0.00')
        self.assertEqual(response.data['choices'][1]['percentage'], '0.00')

    def test_poll_results_return_404_for_missing_poll(self):
        url = reverse('poll-results', kwargs={'pk': 9999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_anonymous_cannot_vote(self):
        url = reverse('vote-list-create')
        data = {
            'poll': self.poll.id,
            'choice': self.choice1.id
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_poll_results_return_correct_percentages(self):
        Vote.objects.create(
            poll=self.poll,
            choice=self.choice1,
            user=self.other_user
        )

        third_user = User.objects.create_user(
            username='thirduser_percent',
            email='[email protected]',
            password='testpass123'
        )

        Vote.objects.create(
            poll=self.poll,
            choice=self.choice2,
            user=third_user
        )

        url = reverse('poll-results', kwargs={'pk': self.poll.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_votes'], 2)
        self.assertEqual(response.data['choices'][0]['percentage'], '50.00')
        self.assertEqual(response.data['choices'][1]['percentage'], '50.00')