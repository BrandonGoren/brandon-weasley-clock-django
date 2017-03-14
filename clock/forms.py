from django import forms
# from django.forms import formset_factory


class LoginForm(forms.Form):
    username = forms.CharField(label='Username')
    password = forms.CharField(label='Password', widget=forms.PasswordInput())


class NewClockForm(forms.Form):
    name = forms.CharField(label='Clock Name')


class StateForm(forms.Form):
    name = forms.CharField(label='State Name')
    position = forms.IntegerField(label='Position')
