from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import LearningQuest, UserProfile


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('A user with that username already exists.')
        return username

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with that email already exists.')
        return email


class UserDetailsForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('An account with that email already exists.')
        return email


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('grade_level', 'school_name', 'avatar')


class LearningQuestForm(forms.ModelForm):
    class Meta:
        model = LearningQuest
        fields = (
            'title',
            'subject',
            'grade_level',
            'question',
            'choice_a',
            'choice_b',
            'choice_c',
            'choice_d',
            'correct_answer',
            'is_published',
        )
        widgets = {
            'question': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        seen_choices = set()
        for field_name in ('choice_a', 'choice_b', 'choice_c', 'choice_d'):
            choice = cleaned_data.get(field_name)
            if not choice:
                continue
            normalized_choice = choice.strip().casefold()
            if normalized_choice in seen_choices:
                self.add_error(field_name, 'Each answer choice must be different.')
            else:
                seen_choices.add(normalized_choice)
        return cleaned_data


class QuestAnswerForm(forms.Form):
    answer = forms.ChoiceField(
        label='Choose your answer',
        widget=forms.RadioSelect,
    )

    def __init__(self, *args, quest, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['answer'].choices = quest.answer_options()
