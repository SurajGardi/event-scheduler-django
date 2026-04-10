from django import forms
from .models import Event
from datetime import datetime

class EventForm(forms.ModelForm):
    HOUR_CHOICES = [(str(h).zfill(2), str(h) + ' ' ) for h in range(1, 13)]
    MINUTE_CHOICES = [(str(m).zfill(2), str(m).zfill(2)) for m in range(0, 60, 5)]
    AMPM_CHOICES = [('AM', 'AM'), ('PM', 'PM')]

    hour = forms.ChoiceField(choices=HOUR_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    minute = forms.ChoiceField(choices=MINUTE_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    ampm = forms.ChoiceField(choices=AMPM_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = Event
        fields = ['name', 'date', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.instance_id = self.instance.pk if self.instance and self.instance.pk else None
        if self.instance and self.instance.pk and self.instance.time:
            t = self.instance.time
            hour_24 = t.hour
            minute = t.minute
            if hour_24 == 0:
                self.fields['hour'].initial = '12'
                self.fields['ampm'].initial = 'AM'
            elif hour_24 < 12:
                self.fields['hour'].initial = str(hour_24).zfill(2)
                self.fields['ampm'].initial = 'AM'
            elif hour_24 == 12:
                self.fields['hour'].initial = '12'
                self.fields['ampm'].initial = 'PM'
            else:
                self.fields['hour'].initial = str(hour_24 - 12).zfill(2)
                self.fields['ampm'].initial = 'PM'
            self.fields['minute'].initial = str(minute).zfill(2)

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        hour = cleaned_data.get('hour')
        minute = cleaned_data.get('minute')
        ampm = cleaned_data.get('ampm')

        if hour and minute and ampm:
            hour_int = int(hour)
            minute_int = int(minute)
            if ampm == 'AM':
                if hour_int == 12:
                    hour_24 = 0
                else:
                    hour_24 = hour_int
            else:
                if hour_int == 12:
                    hour_24 = 12
                else:
                    hour_24 = hour_int + 12
            from datetime import time as dtime
            cleaned_data['time'] = dtime(hour_24, minute_int)

        if date and cleaned_data.get('time') and self.user:
            conflict = Event.objects.filter(user=self.user, date=date, time=cleaned_data['time'])
            if self.instance_id:
                conflict = conflict.exclude(pk=self.instance_id)
            if conflict.exists():
                conflicting_event = conflict.first()
                raise forms.ValidationError(
                    f"You already have '{conflicting_event.name}' at this time. Please choose a different time."
                )
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.time = self.cleaned_data['time']
        if commit:
            instance.save()
        return instance
