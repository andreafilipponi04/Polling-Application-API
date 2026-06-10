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
            password='testpass123'
        )

        self.other_user = User.objects.create_user(
            username='otheruser',
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

    def test_register_user_success(self):
        url = reverse('register')
        data = {
            'username': 'newuser',
            'password': 'StrongPass123!',
            'password2': 'StrongPass123!'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_user_password_mismatch(self):
        url = reverse('register')
        data = {
            'username': 'newuser2',
            'password': 'StrongPass123!',
            'password2': 'DifferentPass123!'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password2', response.data)

    def test_register_user_duplicate_username(self):
        url = reverse('register')
        data = {
            'username': 'testuser',
            'password': 'StrongPass123!',
            'password2': 'StrongPass123!'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_register_then_get_jwt_token(self):
        register_url = reverse('register')
        register_data = {
            'username': 'jwtuser',
            'password': 'StrongPass123!',
            'password2': 'StrongPass123!'
        }

        register_response = self.client.post(register_url, register_data, format='json')
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)

        token_url = reverse('token_obtain_pair')
        token_data = {
            'username': 'jwtuser',
            'password': 'StrongPass123!'
        }

        token_response = self.client.post(token_url, token_data, format='json')

        self.assertEqual(token_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', token_response.data)
        self.assertIn('refresh', token_response.data)

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

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

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
            'question': 'Domanda modificata'
        }

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.poll.refresh_from_db()
        self.assertEqual(self.poll.question, 'Domanda modificata')

    def test_other_user_cannot_update_poll(self):
        self.client.force_authenticate(user=self.other_user)

        url = reverse('poll-detail', kwargs={'pk': self.poll.pk})
        data = {
            'question': 'Tentativo modifica non autore'
        }

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_user_can_vote_once(self):
        self.client.force_authenticate(user=self.other_user)

        url = reverse('vote-create')
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

        url = reverse('vote-create')
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

        url = reverse('vote-create')
        data = {
            'poll': self.poll.id,
            'choice': other_choice.id
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_anonymous_cannot_vote(self):
        url = reverse('vote-create')
        data = {
            'poll': self.poll.id,
            'choice': self.choice1.id
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

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

        choices = response.data['choices']
        pizza = next(c for c in choices if c['text'] == 'Pizza')
        pasta = next(c for c in choices if c['text'] == 'Pasta')

        self.assertEqual(pizza['votes_count'], 2)
        self.assertEqual(pasta['votes_count'], 0)

    def test_poll_results_return_zero_percentages_when_no_votes(self):
        url = reverse('poll-results', kwargs={'pk': self.poll.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_votes'], 0)

        choices = response.data['choices']
        pizza = next(c for c in choices if c['text'] == 'Pizza')
        pasta = next(c for c in choices if c['text'] == 'Pasta')

        self.assertEqual(pizza['percentage'], '0.00')
        self.assertEqual(pasta['percentage'], '0.00')

    def test_poll_results_return_correct_percentages(self):
        Vote.objects.create(
            poll=self.poll,
            choice=self.choice1,
            user=self.other_user
        )

        third_user = User.objects.create_user(
            username='thirduser_percent',
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

        choices = response.data['choices']
        pizza = next(c for c in choices if c['text'] == 'Pizza')
        pasta = next(c for c in choices if c['text'] == 'Pasta')

        self.assertEqual(pizza['percentage'], '50.00')
        self.assertEqual(pasta['percentage'], '50.00')

    def test_poll_results_return_404_for_missing_poll(self):
        url = reverse('poll-results', kwargs={'pk': 9999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_jwt_token(self):
        url = reverse('token_obtain_pair')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_refresh_jwt_token(self):
        obtain_url = reverse('token_obtain_pair')
        obtain_response = self.client.post(
            obtain_url,
            {
                'username': 'testuser',
                'password': 'testpass123'
            },
            format='json'
        )

        self.assertEqual(obtain_response.status_code, status.HTTP_200_OK)
        self.assertIn('refresh', obtain_response.data)

        refresh_url = reverse('token_refresh')
        refresh_response = self.client.post(
            refresh_url,
            {'refresh': obtain_response.data['refresh']},
            format='json'
        )

        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', refresh_response.data)

    def test_verify_jwt_token(self):
        obtain_url = reverse('token_obtain_pair')
        obtain_response = self.client.post(
            obtain_url,
            {
                'username': 'testuser',
                'password': 'testpass123'
            },
            format='json'
        )

        self.assertEqual(obtain_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', obtain_response.data)

        verify_url = reverse('token_verify')
        verify_response = self.client.post(
            verify_url,
            {'token': obtain_response.data['access']},
            format='json'
        )

        self.assertEqual(verify_response.status_code, status.HTTP_200_OK)

    def test_admin_can_update_any_poll(self):
        admin_user = User.objects.create_user(
            username='adminuser',
            password='adminpass123',
            is_staff=True
        )

        self.client.force_authenticate(user=admin_user)

        url = reverse('poll-detail', kwargs={'pk': self.poll.pk})
        data = {
            'question': 'Modifica da admin'
        }

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.poll.refresh_from_db()
        self.assertEqual(self.poll.question, 'Modifica da admin')

    def test_poll_list_is_paginated(self):
        Poll.objects.create(question='Sondaggio 2', created_by=self.user, is_active=True)
        Poll.objects.create(question='Sondaggio 3', created_by=self.user, is_active=True)
        Poll.objects.create(question='Sondaggio 4', created_by=self.user, is_active=True)
        Poll.objects.create(question='Sondaggio 5', created_by=self.user, is_active=True)
        Poll.objects.create(question='Sondaggio 6', created_by=self.user, is_active=True)

        url = reverse('poll-list-create')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('results', response.data)
        self.assertEqual(response.data['count'], 6)

    def test_poll_list_can_be_filtered_by_is_active(self):
        Poll.objects.create(
            question='Sondaggio inattivo',
            created_by=self.user,
            is_active=False
        )

        url = reverse('poll-list-create') + '?is_active=true'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)

        questions = [poll['question'] for poll in response.data['results']]
        self.assertIn('Pizza o pasta?', questions)
        self.assertNotIn('Sondaggio inattivo', questions)

    def test_author_can_create_choice_for_own_poll(self):
        self.client.force_authenticate(user=self.user)

        url = reverse('choice-create')
        data = {
            'poll': self.poll.id,
            'text': 'Risotto'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Choice.objects.filter(poll=self.poll, text='Risotto').exists())

    def test_other_user_cannot_create_choice_for_foreign_poll(self):
        self.client.force_authenticate(user=self.other_user)

        url = reverse('choice-create')
        data = {
            'poll': self.poll.id,
            'text': 'Risotto'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_cannot_create_choice(self):
        url = reverse('choice-create')
        data = {
            'poll': self.poll.id,
            'text': 'Risotto'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_poll_list_search_by_question_partial(self):
        url = reverse('poll-list-create') + '?search=past'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        questions = [poll['question'] for poll in response.data['results']]
        self.assertIn('Pizza o pasta?', questions)

    def test_poll_list_search_by_choice_text_partial(self):
        url = reverse('poll-list-create') + '?search=Pizz'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        questions = [poll['question'] for poll in response.data['results']]
        self.assertIn('Pizza o pasta?', questions)

    def test_poll_list_search_no_results(self):
        url = reverse('poll-list-create') + '?search=Sushi'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

    def test_anonymous_can_view_poll_detail(self):
        url = reverse('poll-detail', kwargs={'pk': self.poll.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.poll.id)
        self.assertEqual(response.data['question'], self.poll.question)

    def test_poll_detail_returns_404_for_missing_poll(self):
        url = reverse('poll-detail', kwargs={'pk': 9999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_author_can_delete_own_poll(self):
        self.client.force_authenticate(user=self.user)

        url = reverse('poll-detail', kwargs={'pk': self.poll.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Poll.objects.filter(pk=self.poll.pk).exists())

    def test_other_user_cannot_delete_poll(self):
        self.client.force_authenticate(user=self.other_user)

        url = reverse('poll-detail', kwargs={'pk': self.poll.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Poll.objects.filter(pk=self.poll.pk).exists())

    def test_admin_can_delete_any_poll(self):
        admin_user = User.objects.create_user(
            username='adminuser_delete',
            password='adminpass123',
            is_staff=True
        )

        self.client.force_authenticate(user=admin_user)

        url = reverse('poll-detail', kwargs={'pk': self.poll.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Poll.objects.filter(pk=self.poll.pk).exists())

    def test_poll_list_can_be_filtered_by_created_by(self):
        Poll.objects.create(
            question='Sondaggio di altro utente',
            created_by=self.other_user,
            is_active=True
        )

        url = reverse('poll-list-create') + '?created_by=testuser'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        questions = [poll['question'] for poll in response.data['results']]
        self.assertIn('Pizza o pasta?', questions)
        self.assertNotIn('Sondaggio di altro utente', questions)

    def test_poll_list_can_be_ordered_by_created_at_ascending(self):
        first = self.poll
        second = Poll.objects.create(
            question='Sondaggio successivo',
            created_by=self.user,
            is_active=True
        )

        url = reverse('poll-list-create') + '?ordering=created_at'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['id'], first.id)
        self.assertEqual(response.data['results'][1]['id'], second.id)

    def test_poll_list_can_be_ordered_by_created_at_descending(self):
        first = self.poll
        second = Poll.objects.create(
            question='Sondaggio successivo 2',
            created_by=self.user,
            is_active=True
        )

        url = reverse('poll-list-create') + '?ordering=-created_at'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['id'], second.id)
        self.assertEqual(response.data['results'][1]['id'], first.id)

    def test_cannot_create_poll_without_question(self):
        self.client.force_authenticate(user=self.user)

        url = reverse('poll-list-create')
        data = {
            'is_active': True
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('question', response.data)

    def test_cannot_create_choice_without_text(self):
        self.client.force_authenticate(user=self.user)

        url = reverse('choice-create')
        data = {
            'poll': self.poll.id
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('text', response.data)

    def test_poll_list_page_size_query_param_works(self):
        for i in range(6, 11):
            Poll.objects.create(
                question=f'Sondaggio {i}',
                created_by=self.user,
                is_active=True
            )

        url = reverse('poll-list-create') + '?page_size=3'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)

    def test_cannot_vote_on_closed_poll(self):
        self.client.force_authenticate(user=self.user)

        closed_poll = Poll.objects.create(
            question="Sondaggio chiuso",
            created_by=self.user,
            is_active=False
        )

        choice = Choice.objects.create(
            poll=closed_poll,
            text="Opzione 1"
        )

        payload = {
            "poll": closed_poll.id,
            "choice": choice.id
        }

        response = self.client.post("/api/votes/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("poll", response.data)