from .models import Clock, LocationCondition, CurrentState, State, UserProfile
from .forms import LoginForm, NewClockForm, StateForm
from django.contrib.auth import authenticate, login, logout
from geopy.distance import great_circle
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.core import serializers
from django.shortcuts import render, redirect
from django.forms import formset_factory, modelformset_factory


def index(request):
	if request.user.is_authenticated:
		context = {
		'clocks': Clock.objects.filter(userProfiles__user=request.user),
		'user_profile': UserProfile.objects.get(user=request.user)
		}
		return render(request, 'clock/index.html', context)
	else:
		context = {'form': LoginForm()}
		return render(request, 'clock/sign-in.html', context)


def login_user(request):
	username = request.POST['username']
	password = request.POST['password']
	user = authenticate(username=username, password=password)
	if user is not None:
		login(request, user)
		return redirect('index')
	else:
		return render(request, 'clock/sign-in.html', {'form': LoginForm()})


def logout_user(request):
	logout(request)
	return redirect('index')


def clock_view(request, clock_id):
	clock = Clock.objects.get(id=clock_id)
	states = State.objects.filter(clock=clock)
	current_states = CurrentState.objects.filter(clock=clock)
	context = {
		'clock': clock,
		'states': states,
		'current_states': current_states
	}
	return render(request, 'clock/clock-view.html', context)

def create_clock_form(request):
	if request.user.is_authenticated:
		context = {'form': NewClockForm()}
		return render(request, 'clock/create-clock.html', context)
	else:
		context = {'form': LoginForm()}
		return render(request, 'clock/sign-in.html', context)

def create_clock_object(request):
	name = request.POST['name']
	clock = Clock.objects.create(name_text=name)
	requester_profile = UserProfile.objects.get(user__username=request.user)
	clock.userProfiles.add(requester_profile)
	clock.save()
	CurrentState.objects.create(clock=clock, userProfile=requester_profile)
	return redirect('clock/{0}'.format(clock.id))


@csrf_exempt
def update_location(request):
	username = request.POST['username']
	latitude = request.POST['latitude']
	longitude = request.POST['longitude']
	location_conditions = LocationCondition.objects.filter(userProfile__user__username=username)
	potential_clock_states_to_change = []
	for condition in location_conditions:
		if great_circle((latitude, longitude), (condition.latitude_dec, condition.longitude_dec)).miles <= \
				condition.radius_miles:
			potential_clock_states_to_change.append((condition.state.clock, condition.state))
	for clockState in potential_clock_states_to_change:
		current_state = CurrentState.objects.get(clock=clockState[0], userProfile__user__username=username)
		current_state.state = clockState[1]
		current_state.lastChanged_datetime = timezone.now()
		current_state.save()
	return HttpResponse(status=200)


def get_states_from_clock_id(request, clock_id):
		username = request.POST['username']
		clock = Clock.objects.get(id=clock_id)
		if clock.has_permission(username):
			return HttpResponse(serializers.serialize('json', State.objects.filter(clock__id=clock_id)))
		else:
			return HttpResponse(status=550)


def get_current_states_from_clock_id(request, clock_id):
	username = request.POST['username']
	clock = Clock.objects.get(id=clock_id)
	if clock.has_permission(username):
		return HttpResponse(serializers.serialize('json', CurrentState.objects.filter(clock__id=clock_id)))
	else:
		return HttpResponse(status=550)


def get_user_profiles_from_clock_id(request, clock_id):
	username = request.POST('username')
	clock = Clock.objects.get(id=clock_id)
	if clock.has_permission(username):
		return HttpResponse(serializers.serialize('json', clock.userProfiles.all()))
	else:
		return HttpResponse(status=550)

def add_user_to_clock(requester, clock_id):
	user_profile = UserProfile.objects.get(user__username=requester)
	clock = Clock.objects.get(id=clock_id)
	clock.UserProfiles.add(user_profile)
	clock.save()
	CurrentState.objects.create(clock=clock, userProfile=user_profile)
	return HttpResponse(status=200)

def manage_states(request, clock_id):
	ManageStates = modelformset_factory(State, exclude=('id','clock'))
	states = State.objects.filter(clock__id=clock_id)
	formset = ManageStates(queryset=states)
	return render(request, 'clock/manage-states.html', {
	'formset': formset
	})

def manage_states_post(request):
	print request.POST
	return HttpResponse(status=200)

def create_state(request, clock_id):
	name = request.POST['name']
	position = request.POST['position']
	clock = Clock.objects.get(id=clock_id)
	State.objects.create(clock=clock, name_text=name, position_int=position)
	return HttpResponse(status=200)


def update_current_state(request):
	current_state_id = request.POST['current_state_id']
	state_id = request.POST['state_id']
	state = State.objects.get(id=state_id)
	current_state = CurrentState.objects.get(id=current_state_id)
	current_state.state = state
	current_state.lastChanged_datetime = timezone.now()
	current_state.save()
	return HttpResponse(status=200)
