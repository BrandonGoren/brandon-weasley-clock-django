from django.test import TestCase
from clock.models import UserProfile, Clock, State, CurrentState, LocationCondition
from geopy.distance import great_circle
from django.utils import timezone
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.test import Client


class FilterTest(TestCase):
	def setUp(self):
		brandon_user = User.objects.create_user(username='brandon')
		john_user = User.objects.create_user(username='John')
		brandon_profile = UserProfile.objects.create(user=brandon_user, display_name_text='Brandon Goren')
		john_profile = UserProfile.objects.create(user=john_user, display_name_text='John Lennon')
		test_clock = Clock.objects.create(name_text='clock')
		test_clock.userProfiles.add(brandon_profile, john_profile)
		test_clock.save()
		home = State.objects.create(clock=test_clock, name_text='home')
		work = State.objects.create(clock=test_clock, name_text='work')
		CurrentState.objects.create(userProfile=brandon_profile, clock=test_clock, state=work)
		CurrentState.objects.create(userProfile=john_profile, clock=test_clock, state=home)
		LocationCondition.objects.create(state=home, userProfile=brandon_profile, longitude_dec=30, latitude_dec=30, radius_miles=1)

	def test_http_response(self):
		c = Client()
		print('*** Start HTTP Response ***')
		response = c.post('/clock/1/current-states/', {'username': 'brandong'})
		print(response)
		print('*** End HTTP Response ***')
		return True

	def test_location_base_case(self):
		latitude = 30
		longitude = 30
		username = 'brandon'
		print('*** Location Base Case ***')
		location_conditions = LocationCondition.objects.filter(userProfile__user__username=username)
		potential_clock_states_to_change = []
		for condition in location_conditions:
			if great_circle((latitude, longitude), (condition.latitude_dec, condition.longitude_dec)).miles < condition.radius_miles:
				potential_clock_states_to_change.append((condition.state.clock, condition.state))
		for clock_state in potential_clock_states_to_change:
			current_state = CurrentState.objects.get(clock=clock_state[0], userProfile__user__username=username)
			current_state.state = clock_state[1]
			current_state.lastChanged_datetime = timezone.now()
			current_state.save()
		json_states = []
		for state in State.objects.all():
			json_states.append(state.json_dictionary())
		JsonResponse(json_states, safe=False)
		return True
		# print JsonResponse(json_states, safe=False)
		# print JsonResponse(State.objects.filter(clock__id_int=1).values(), safe=False)
		# print views.getStatesFromClockId(HttpRequest)
		# print State.objects.all(), fields('name_text','current_state_to_state__userProfile')
		# HttpResponse(serializers.serialize('json', State.objects.all(), fields=('name_text','position_int')))
