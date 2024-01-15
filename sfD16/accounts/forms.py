from django import forms
from allauth.account.forms import SignupForm
from .models import UserProfile
import pytz



class CustomSignupForm(SignupForm):
    timezone = forms.ChoiceField(choices=[(x,x) for x in pytz.common_timezones])

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        UserProfile.objects.create(user=user, timezone= self.cleaned_data['timezone'])
        user.save()
        return user