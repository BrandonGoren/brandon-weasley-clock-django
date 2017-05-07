from django.forms import ModelForm, Form, PasswordInput, CharField, IntegerField, ValidationError
from django.forms.formsets import BaseFormSet
from clock.models import Clock, State, LocationCondition


class LoginForm(Form):
    username = CharField(label='Username')
    password = CharField(label='Password', widget=PasswordInput())


class ClockForm(ModelForm):

    class Meta:
        model = Clock
        fields = ('name', 'description')


class LocationConditionForm(ModelForm):

    class Meta:
        model = LocationCondition
        fields = ('state', 'place_name')


class StateForm(ModelForm):

    class Meta:
        model = State
        fields = ('name', 'position')


class BaseStateFormSet(BaseFormSet):
    def clean(self):
        if any(self.errors):
            return
        positions = []
        duplicate_positions = False
        for form in self.forms:
            if form.cleaned_data:
                position = form.cleaned_data['position']

                if position in positions:
                    raise forms.ValidationError('There cannot be two states with the same position.',
                    code='duplicate positions'
                    )
                else:
                    positions.append(position)
