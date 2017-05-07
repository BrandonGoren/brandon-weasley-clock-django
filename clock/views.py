from .models import Clock, LocationCondition, CurrentState, State, UserProfile
from .forms import LoginForm, ClockForm, StateForm, LocationConditionForm
from django.contrib.auth import authenticate, login, logout
from geopy.distance import great_circle
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.core import serializers
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
from django.forms import formset_factory, modelformset_factory


def index(request):
    if request.user.is_authenticated:
        context = {
            'clocks': Clock.objects.filter(user_profiles__user=request.user).order_by('name'),
            'user_profile': UserProfile.objects.get(user=request.user)
        }
        return render(request, 'clock/index.html', context)
    else:
        context = {'form': LoginForm()}
        return render(request, 'clock/sign-in.html', context)


def clock_view(request, clock_id):
    clock = Clock.objects.get(id=clock_id)
    states = State.objects.filter(clock=clock)
    current_states = CurrentState.objects.filter(
        clock=clock).order_by('position')
    context = {
        'clock': clock,
        'states': states,
        'current_states': current_states
    }
    return render(request, 'clock/clock-view.html', context)


def clock_form(request, clock_id=None):
    if request.user.is_authenticated:
        new_clock = clock_id is None
        if request.method == 'POST':
            if new_clock:
                form = ClockForm(request.POST)
            else:
                clock = Clock.objects.get(id=clock_id)
                form = ClockForm(request.POST, instance=clock)
            if form.is_valid():
                clock = form.save()
                if new_clock:
                    requester_profile = UserProfile.objects.get(
                        user=request.user)
                    clock.user_profiles.add(requester_profile)
                    clock.save()
                    State.objects.create(clock=clock, name='Home', position=0)
                    State.objects.create(clock=clock, name='Work', position=4)
                    State.objects.create(
                        clock=clock, name='Mortal Peril', position=8)
                    CurrentState.objects.create(
                        clock=clock, user_profile=requester_profile)
                return redirect('/clock/{id}'.format(id=clock.id))
            else:
                return render(request, 'clock/clock-form.html', {'form': form})
        else:
            if new_clock:
                form = ClockForm()
            else:
                clock = Clock.objects.get(id=clock_id)
                form = ClockForm(instance=clock)
            return render(request, 'clock/clock-form.html', {'form': form})
    else:
        context = {'form': LoginForm()}
        return render(request, 'clock/sign-in.html', context)


def location_condition_form(request, clock_id, location_condition_id=None):
    new_location_condition = location_condition_id is None
    clock = Clock.objects.get(id=clock_id)
    if request.method == 'POST':
        if new_location_condition:
            form = LocationConditionForm(request.POST)
        else:
            location_condition = LocationCondition.objects.get(
                id=location_condition_id)
            form = LocationConditionForm(
                request.POST, instance=location_condition)
        if form.is_valid():
            location_condition = form.save(commit=False)
            location_condition.radius_miles = request.POST.get('radius_miles')
            location_condition.latitude = request.POST.get('latitude')
            location_condition.longitude = request.POST.get('longitude')
            if new_location_condition:
                requester_profile = UserProfile.objects.get(
                    user=request.user)
                location_condition.user_profile = requester_profile
            location_condition.save()
        return redirect('/clock/{id}/location-conditions/'.format(id=clock_id))
    else:
        if new_location_condition:
            form = LocationConditionForm()
        else:
            location_condition = LocationCondition.objects.get(
                id=location_condition_id)
            form = LocationConditionForm(instance=location_condition)
        form.fields['state'].queryset = State.objects.filter(clock=clock)
        return render(request,
                      'clock/location-condition-form.html',
                      {'form': form, 'clock': clock})


def delete_clock(request):
    if request.user.is_authenticated and request.method == 'POST':
        clock = Clock.objects.get(id=request.POST.get('clock_id'))
        if clock.has_permission(request.user.username):
            clock.delete()
            return redirect('/')
    return HttpResponse(status=550)


def delete_location_condition(request):
    if request.user.is_authenticated and request.method == 'POST':
        location_condition = LocationCondition.objects.get(
            id=request.POST.get('location_condition_id'))
        if (location_condition.user_profile.user == request.user):
            location_condition.delete()
            return redirect('/clock/{id}/location-conditions/'.format(id=request.POST.get('clock_id')))
    return HttpResponse(status=550)


def manage_states(request, clock_id):
    StateFormSet = modelformset_factory(
        State, exclude=('id', 'clock'), can_delete=True)
    clock = Clock.objects.get(id=clock_id)
    if request.method == 'GET':
        states = State.objects.filter(clock__id=clock_id)
        formset = StateFormSet(queryset=states)
        return render(request, 'clock/manage-states.html', {
            'clock': clock,
            'formset': formset
        })
    else:
        formset = StateFormSet(request.POST, request.FILES)
        if formset.is_valid():
            for form in formset:
                if form.is_valid():
                    if form.empty_permitted:
                        if form.instance.name and form.instance.position is not None:
                            state = form.save(commit=False)
                            state.clock = clock
                            state.save()
                    else:
                        form.save()
            for form in formset.deleted_forms:
                if form.instance.id:
                    form.instance.delete()
    return redirect('/clock/{id}'.format(id=clock_id))


@csrf_exempt
def update_location(request):
    username = request.POST['username']
    latitude = request.POST['latitude']
    longitude = request.POST['longitude']
    location_conditions = LocationCondition.objects.filter(
        user_profile__user__username=username)
    potential_clock_states_to_change = []
    for condition in location_conditions:
        if great_circle((latitude, longitude), (condition.latitude, condition.longitude)).miles <= \
                condition.radius_miles:
            potential_clock_states_to_change.append(
                (condition.state.clock, condition.state))
    for clock_state in potential_clock_states_to_change:
        current_state = CurrentState.objects.get(
            clock=clock_state[0], user_profile__user__username=username)
        current_state.state = clock_state[1]
        current_state.save()
    return HttpResponse(status=200)


def login_user(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect('index')
    else:

        return render(request, 'clock/sign-in.html', {'form': LoginForm(), 'error': 'Invaild username or password'})


def logout_user(request):
    logout(request)
    return redirect('index')


class LocationConditionList(ListView):
    context_object_name = 'location_conditions'
    template_name = 'clock/location-condition-list.html'

    def get_queryset(self):
        self.clock = get_object_or_404(Clock, id=self.kwargs['clock_id'])
        return LocationCondition.objects.filter(state__clock=self.clock)

    def get_context_data(self, **kwargs):
        context = super(LocationConditionList, self).get_context_data(**kwargs)
        # Add in the publisher
        context['clock'] = self.clock
        return context
