from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.contrib import messages

from .models import *
from .forms import CreateUserForm

def registerPage(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        form = CreateUserForm()

        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('username')
                messages.success(request, 'Account was created for ' + user )
                return redirect('login')

        context = {'form':form}

        return render(request, 'funo/register.html', context)

def loginPage(request):
    if request.user.is_authenticated:
         return redirect('dashboard')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request,user)
                return redirect('dashboard')
            else:
                messages.info(request, 'Username OR password is incorrect')

        context = {}

        return render(request, 'funo/login.html', context)


def logoutUser(request):
	logout(request)
	return redirect('login')


@login_required(login_url='login')
def dashboard(request):
    return render(request, 'funo/dashboard.html')


@login_required(login_url='login')
def user(request):
    return render(request, 'funo/user.html')


@login_required(login_url='login')
def support(request):
    return render(request, 'funo/support.html')


@login_required(login_url='login')
def aboutus(request):
    return render(request, 'funo/aboutus.html')


@login_required(login_url='login')
def subscription(request):
    return render(request, 'funo/subscription.html')
