from django.forms import ModelForm, Form, PasswordInput, CharField, IntegerField
from clock.models import Clock


class LoginForm(Form):
    username = CharField(label='Username')
    password = CharField(label='Password', widget=PasswordInput())


class ClockForm(ModelForm):
    # name = forms.CharField(label='Clock Name')
    # description = forms.CharField(label='Description')

    class Meta:
        model = Clock
        fields = ['name', 'description']


class StateForm(Form):
    name = CharField(label='State Name')
    position = IntegerField(label='Position')
