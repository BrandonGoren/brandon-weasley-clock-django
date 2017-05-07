from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=200)
    avatar = models.ImageField(blank=True, null=True)

    def __str__(self):
        return '{0} ({1})'.format(self.display_name, self.user.username)


class Clock(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=200, null=True)
    description = models.CharField(max_length=500, null=True, blank=True)
    user_profiles = models.ManyToManyField(
        UserProfile, related_name='users_clock')

    def has_permission(self, username):
        return username in str(self.user_profiles.all())

    def __str__(self):
        return self.name


class State(models.Model):
    id = models.AutoField(primary_key=True)
    clock = models.ForeignKey(Clock, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    position = models.IntegerField(default=0)

    def get_user_profiles_in_state(self):
        return self.current_state_to_state.all().values('user_profile__display_name')

    def __str__(self):
        return '{0} - {1}'.format(self.clock.name, self.name)


class CurrentState(models.Model):
    id = models.AutoField(primary_key=True)
    user_profile = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name='user_state')
    clock = models.ForeignKey(Clock, on_delete=models.CASCADE)
    state = models.ForeignKey(
        State, on_delete=models.CASCADE, null=True, related_name='current_state_to_state')
    priority = models.IntegerField(default=0)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.state:
            return "{0}'s State for {1} ({2})".format(self.user_profile.display_name, self.clock.name, self.state.name)
        else:
            return "{0}'s State for {1}".format(self.user_profile.display_name, self.clock.name)


class LocationCondition(models.Model):
    id = models.AutoField(primary_key=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    user_profile = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name='user_locationCondition')
    place_name = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    radius_miles = models.FloatField()
    priority = models.IntegerField(default=1)

    def __str__(self):
        return '{0} - {1} ({2}): ({3}, {4})'\
            .format(self.user_profile.display_name, self.state.name, self.state.clock.name, self.latitude, self.longitude)
