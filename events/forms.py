from django import forms
from .models import Event

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'date', 'time', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.instance_id = self.instance.pk if self.instance and self.instance.pk else None

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')
        if date and time and self.user:
            conflict = Event.objects.filter(user=self.user, date=date, time=time)
            if self.instance_id:
                conflict = conflict.exclude(pk=self.instance_id)
            if conflict.exists():
                conflicting_event = conflict.first()
                raise forms.ValidationError(
                    f"You already have '{conflicting_event.name}' at this time. Please choose a different time."
                )
        return cleaned_data
