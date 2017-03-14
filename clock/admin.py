from django.contrib import admin
from clock.models import UserProfile, Clock, State, CurrentState, LocationCondition

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Clock)
admin.site.register(State)
admin.site.register(CurrentState)
admin.site.register(LocationCondition)
