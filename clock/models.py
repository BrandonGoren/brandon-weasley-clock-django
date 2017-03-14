from __future__ import unicode_literals
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	display_name_text = models.CharField(max_length=200)
	avatar = models.ImageField(blank=True, null=True)
	avatar_source_text = models.URLField(null=True)

	def __str__(self):
		return str(self.user)


class Clock(models.Model):
	id = models.AutoField(primary_key=True)
	name_text = models.CharField(max_length=200)
	code_text = models.CharField(max_length=200, null=True)
	userProfiles = models.ManyToManyField(UserProfile, related_name='users_clock')

	def has_permission(self, username):
		return username in str(self.userProfiles.all())

	def __str__(self):
		return self.name_text


class State(models.Model):
	id = models.AutoField(primary_key=True)
	clock = models.ForeignKey(Clock, on_delete=models.CASCADE)
	name_text = models.CharField(max_length=200)
	position_int = models.IntegerField(default=0)

	def get_user_profiles_in_state(self):
		return self.current_state_to_state.all().values('userProfile__display_name_text')

	def json_dictionary(self):
		return {
			'id': self.id,
			'name_text': self.name_text,
			'position_int': self.position_int,
			'userProfiles': list(self.get_user_profiles_in_state())
			}

	def __str__(self):
		return '{0} - {1}'.format(self.clock.name_text, self.name_text)


class CurrentState(models.Model):
	id = models.AutoField(primary_key=True)
	userProfile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='user_state')
	clock = models.ForeignKey(Clock, on_delete=models.CASCADE)
	state = models.ForeignKey(State, on_delete=models.CASCADE, null=True, related_name='current_state_to_state')
	priority = models.IntegerField(default=0)
	last_changed_datetime = models.DateTimeField(default=timezone.now)

	def __str__(self):
		return '{0} State for {1} - {2}'.format(self.userProfile, self.clock.name_text, self.state.name_text)


class LocationCondition(models.Model):
	id = models.AutoField(primary_key=True)
	state = models.ForeignKey(State, on_delete=models.CASCADE)
	userProfile = models.ForeignKey(UserProfile, on_delete = models.CASCADE, related_name='user_locationCondition')
	latitude_dec = models.DecimalField(max_digits=9, decimal_places=6)
	longitude_dec = models.DecimalField(max_digits=9, decimal_places=6)
	radius_miles = models.FloatField()
	priority = models.IntegerField(default=1)

	def __str__(self):
		return '{0} - {1} ({2}): ({3}, {4})'\
			.format(self.userProfile, self.state.name_text, self.state.clock.name_text, self.latitude_dec, self.longitude_dec)
