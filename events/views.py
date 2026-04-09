from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Event
from .forms import EventForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect('event_list')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.username}! Your account has been created.")
            return redirect('event_list')
        else:
            messages.error(request, "Registration failed. Please correct the errors below.")
    else:
        form = UserCreationForm()
    return render(request, 'events/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('event_list')
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('event_list')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'events/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('login')


@login_required
def event_list(request):
    events = Event.objects.filter(user=request.user)
    return render(request, 'events/event_list.html', {'events': events})


@login_required
def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk, user=request.user)
    return render(request, 'events/event_detail.html', {'event': event})


@login_required
def event_create(request):
    if request.method == 'POST':
        form = EventForm(request.POST, user=request.user)
        if form.is_valid():
            event = form.save(commit=False)
            event.user = request.user
            event.save()
            messages.success(request, f"Event '{event.name}' has been created successfully!")
            return redirect('event_list')
    else:
        form = EventForm(user=request.user)
    return render(request, 'events/event_form.html', {'form': form, 'title': 'Create Event'})


@login_required
def event_update(request, pk):
    event = get_object_or_404(Event, pk=pk, user=request.user)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f"Event '{event.name}' has been updated successfully!")
            return redirect('event_list')
    else:
        form = EventForm(instance=event, user=request.user)
    return render(request, 'events/event_form.html', {'form': form, 'title': 'Update Event'})


@login_required
def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk, user=request.user)
    if request.method == 'POST':
        name = event.name
        event.delete()
        messages.success(request, f"Event '{name}' has been deleted.")
        return redirect('event_list')
    return render(request, 'events/event_confirm_delete.html', {'event': event})
