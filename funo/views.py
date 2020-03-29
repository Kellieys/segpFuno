from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
from .forms import CreateUserForm, SupportForm,UpdateProfileForm
from django.shortcuts import render
from django.contrib.auth import get_user_model
from keras import backend
from keras.models import load_model
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import api_view
from django.conf import settings
from django.views.generic import View
from keras import backend as K
from pickle import load

User = get_user_model()
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
                password = form.cleaned_data.get('password1')
                company = form.cleaned_data.get('company')
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


def fill_missing(past_data):
        for row in range(past_data.shape[0]):
            for col in range(past_data.shape[1]):
                if np.isnan(past_data[row, col]):
                    i = 1
                    missing_next = past_data[row + i, col]
                    while(np.isnan(missing_next)):
                        i += 1
                        missing_next = past_data[row + i, col]
                    past_data[row, col] = past_data[row - 1, col] + ((missing_next - past_data[row - 1, col]) / (i+1))
                    
def data_Predict(request,*args,**kwargs):
        K.clear_session()
        my_thing = request.session.get('data', None)
        past_data = pd.read_csv(my_thing['dataFile'])
        regressor = load_model(my_thing['modelFile'])
        scaler = load(open(my_thing['scalerFile'], 'rb'))
        duration = my_thing['duration']
        forecast= my_thing['forecast']
        current= my_thing['current']
        title=my_thing['title']        
        print(current)

        date=past_data['Date'].iloc[-current:]
        date=pd.to_datetime(date).tolist()
        if forecast==0:
            date=date
            past_data.set_index(['Date'], inplace= True)
            fill_missing(past_data.values)
            past_data = past_data.round(2)
            past_price = past_data.loc[:]['Harga Ladang'].round(2)
            past_price = past_data['Harga Ladang'].iloc[-current:].round(2)
            past_price = list(map(str, past_price))

            date = list(map(str, date))
            for i in range (0, len(date)):
                date[i] = date[i].split(' ')[0]
            data={
                'forecast':forecast,
                'title':title,
                'labels':','.join(date),
                'default': ','.join(past_price)
            }
        else:
            date2=past_data["Date"].iloc[-1]
            date2=pd.Series(pd.date_range(date2, periods=forecast+1, freq='7D'))
            date2=date2[1:].tolist()   
            date=date + date2
        
            past_data.set_index(['Date'], inplace= True)
            fill_missing(past_data.values)
            past_data = past_data.round(2)
            past_price = past_data.loc[:]['Harga Ladang'].round(2)
        
            date = list(map(str, date))
            for i in range (0, len(date)):
                date[i] = date[i].split(' ')[0]
            feedin_price = []
            feedin_price.append(past_price[(len(past_price)-52):])
            feedin_price = np.array(feedin_price)

            feedin_price_scaled = scaler.transform(feedin_price.reshape(-1, 1))
            feedin_price_scaled = feedin_price_scaled.reshape(1, feedin_price_scaled.shape[0], 1)
            
            future_price = regressor.predict(feedin_price_scaled)
            future_price = scaler.inverse_transform(future_price)
            future_price = future_price.reshape(-1 ,1)
        
            future_price=future_price.round(2).tolist()
            func = lambda x: round(x,2)
            future_price = [list(map(func, i)) for i in future_price]
            past_price = past_data['Harga Ladang'].iloc[-current:].round(2)
            past_price= past_price.tolist() + future_price #so I get total_price and date(complete) #future price is 52
            if forecast!=52:
                for i in range(0,(52-forecast)):
                    past_price.pop()

            past_price = list(map(str, past_price))

            for i in range (1, len(past_price)):
                past_price[i] = past_price[i].replace('[', '').replace(']', '')


            data={
                'forecast':forecast,
                'title':title,
                'labels':','.join(date),
                'default': ','.join(past_price)
            }
        print(len(date))
        print(len(past_price))
        K.clear_session()
        return JsonResponse(data)

@login_required(login_url='login')
def dashboard(request):
    dataFile='rawData/poultry/chicken/chicken.csv'
    modelFile='rawData/poultry/chicken/chicken.h5'
    scalerFile = 'rawData/poultry/chicken/chicken.pkl'
    durationVar=0
    forecast=52
    current=260
    title="Chicken Field Price Forecast"
    
    if request.method=='GET':
            commodity=request.GET.get('commodity')
            duration=request.GET.get('duration')
            datatype=request.GET.get('datatype')
            
            if commodity=='coconut':
                dataFile='rawData/coconut/coconut.csv'
                modelFile='rawData/coconut/coconut.h5'
                scalerFile = 'rawData/coconut/coconut.pkl'
                title="Coconut Field Price Forecast"
            
            elif commodity=='kangkung':
                dataFile='rawData/vegetables/kangkung/kangkung.csv'
                modelFile='rawData/vegetables/kangkung/kangkung.h5'
                scalerFile = 'rawData/vegetables/kangkung/kangkung.pkl'
                title="Water Spinach Field Price Forecast"

            elif commodity=='sawiHijau':
                dataFile='rawData/vegetables/sawiHijau/sawiHijau.csv'
                modelFile='rawData/vegetables/sawiHijau/sawiHijau.h5'
                scalerFile = 'rawData/vegetables/sawiHijau/sawiHijau.pkl'
                title="Choy Sum Field Price Forecast"
            
            elif commodity=='tomato':
                dataFile='rawData/fruits/tomato/tomato.csv'
                modelFile='rawData/fruits/tomato/tomato.h5'
                scalerFile = 'rawData/fruits/tomato/tomato.pkl'
                title="Tomato Field Price Forecast"

            elif commodity=='chilli':
                dataFile='rawData/fruits/chilli/chilli.csv'
                modelFile='rawData/fruits/chilli/chilli.h5'
                scalerFile = 'rawData/fruits/chilli/chilli.pkl'
                title="Red Chilli Field Price Forecast"

            elif commodity=='chicken':
                dataFile='rawData/poultry/chicken/chicken.csv'
                modelFile='rawData/poultry/chicken/chicken.h5'
                scalerFile = 'rawData/poultry/chicken/chicken.pkl'
                title="Chicken Field Price Forecast"

            elif commodity=='eggA':
                dataFile='rawData/poultry/eggA/eggA.csv'
                modelFile='rawData/poultry/eggA/eggA.h5'
                scalerFile = 'rawData/poultry/eggA/eggA.pkl'
                title="Egg (Grade A) Field Price Forecast"

            elif commodity=='eggB':
                dataFile='rawData/poultry/eggB/eggB.csv'
                modelFile='rawData/poultry/eggB/eggB.h5'
                scalerFile = 'rawData/poultry/eggB/eggB.pkl'
                title="Egg (Grade B) Field Price Forecast"

            elif commodity=='eggC':
                dataFile='rawData/poultry/eggC/eggC.csv'
                modelFile='rawData/poultry/eggC/eggC.h5'
                scalerFile = 'rawData/poultry/eggC/eggC.pkl'
                title="Egg (Grade C) Field Price Forecast"
            
            elif commodity=="":
                dataFile='rawData/poultry/chicken/chicken.csv'
                modelFile='rawData/poultry/chicken/chicken.h5'
                scalerFile = 'rawData/poultry/chicken/chicken.pkl'
                title="Chicken Field Price Forecast"
            

            if duration=="sixmonth":
                durationVar=26
            
            elif duration=="oneyear":
                durationVar=53
            
            elif duration=="fiveyear":
                durationVar=260

            elif duration=="threeyear": 
                durationVar=156

            elif duration=="tenyear":
                durationVar=520

            elif duration=="":
                durationVar=260
            
            if datatype=="pastdata":
                forecast=0
                current=durationVar-forecast

            elif datatype=="forecast3month":
                if durationVar<13:
                    forecast=13
                    current=forecast
                else:
                    forecast=13
                    current=durationVar-forecast

            elif datatype=="forecast6month":
                if durationVar==26:
                    forecast=26
                    current=1
                else:
                    forecast=26
                    current=durationVar-forecast

            elif datatype=="forecast1year":                    
                if durationVar<52:
                    forecast=52
                    current=1
                else:
                    forecast=52
                    current=durationVar-forecast

            elif datatype=="":
                if durationVar<52:
                    forecast=52
                    current=forecast
                else:
                    forecast=52
                    current=durationVar-forecast
             
            
            print(dataFile)
            data={
                'dataFile':dataFile,
                'modelFile':modelFile,
                'scalerFile':scalerFile,
                'duration':durationVar,
                'forecast':forecast,
                'current':current,
                'title':title
            }
            request.session['data']=data

    context = {'page':'Dashboard'}

    return render(request, 'funo/dashboard.html',context)


@login_required(login_url='login')
def user(request):
    if request.method == 'POST':
            print("HEHE")
            form = UpdateProfileForm(request.POST,instance=request.user.profile)
            if form.is_valid():
                form.save()
                messages.success(request, 'Profile Updated!' )
                return redirect('user')
            else:
                print(form.errors)
            context={
                'user':user,
                'name':request.user.get_username(),
                'form':form,
                'page':'User Profile'
            }
    
    else:
        form = UpdateProfileForm(instance=request.user.profile)
        context={
                'user':user,
                'name':request.user.get_username(),                
                'form':form,
                'page':'User Profile'   
            }    
    
    return render(request, 'funo/user.html',context)


@login_required(login_url='login')
def support(request):
    form = SupportForm()

    if request.method == 'POST':
            form = SupportForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Thanks for reaching us!' )
                return redirect('support')

    context = {'form':form,'page':'Contact Us'}

    return render(request, 'funo/support.html', context)

@login_required(login_url='login')
def weather(request):

    context = {'page':'Weather Forecast'}

    return render(request, 'funo/weather.html', context)


@login_required(login_url='login')
def aboutus(request):

    context = {'page':'About Us'}

    return render(request, 'funo/aboutus.html', context)


@login_required(login_url='login')
def subscription(request):

    context = {'page':'Subscription'}

    return render(request, 'funo/subscription.html', context)


