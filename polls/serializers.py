from rest_framework import serializers
from .models import Poll, Choice, Vote


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'poll', 'text']


class PollSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Poll
        fields = ['id', 'question', 'created_by', 'created_at', 'updated_at', 'is_active', 'choices']


class VoteSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Vote
        fields = ['id', 'poll', 'choice', 'user', 'voted_at']

    def validate(self, attrs):
        request = self.context.get('request')
        poll = attrs.get('poll')
        choice = attrs.get('choice')

        if choice.poll != poll:
            raise serializers.ValidationError({
                'choice': 'La scelta selezionata non appartiene a questo sondaggio.'
            })

        if request and request.user.is_authenticated:
            if Vote.objects.filter(poll=poll, user=request.user).exists():
                raise serializers.ValidationError({
                    'non_field_errors': ['Hai già votato in questo sondaggio.']
                })

        return attrs


class ChoiceResultSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    text = serializers.CharField()
    votes_count = serializers.IntegerField()
    percentage = serializers.DecimalField(max_digits=5, decimal_places=2)


class PollResultSerializer(serializers.Serializer):
    poll_id = serializers.IntegerField()
    question = serializers.CharField()
    total_votes = serializers.IntegerField()
    choices = ChoiceResultSerializer(many=True)