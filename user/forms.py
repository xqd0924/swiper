from django import forms

from user.models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = '__all__'

    def clean_max_dating_age(self):
        cleaned_data = super().clean()
        min_dating_age = cleaned_data['min_dating_age']
        max_dating_age = cleaned_data['max_dating_age']
        if min_dating_age > max_dating_age:
            raise forms.ValidationError('min_dating_age > max_dating_age')
