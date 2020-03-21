from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.contrib import messages

from .models import *
from .forms import CreateUserForm
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
        my_thing = request.session.get('data', None)
        past_data = pd.read_csv(my_thing['dataFile'])
        regressor = load_model(my_thing['modelFile'])
        duration = my_thing['duration']
        forecast= my_thing['forecast']
        current= my_thing['current']
        theForecastValue=[]

        date=past_data['Date'].iloc[-current:]
        date=pd.to_datetime(date).tolist()
        if forecast==0:
            date=date
            past_data.set_index(['Date'], inplace= True)
            fill_missing(past_data.values)
            past_data = past_data.round(2)
            past_price = past_data.loc[:]['Harga Ladang'].round(2)
            past_price = list(map(str, past_price))

            date = list(map(str, date))
            for i in range (0, len(date)):
                date[i] = date[i].split(' ')[0]
            data={
                'labels':','.join(date),
                'default': ','.join(past_price)
            }
        else:
            date2=past_data["Date"].iloc[-1]
            date2=pd.Series(pd.date_range(date2, periods=forecast, freq='7D'))
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

            sc = MinMaxScaler(feature_range = (0, 1))
            feedin_price_scaled = sc.fit_transform(feedin_price.reshape(-1, 1))
            feedin_price_scaled = feedin_price_scaled.reshape(1, feedin_price_scaled.shape[0], 1)
            
            future_price = regressor.predict(feedin_price_scaled)
            future_price = sc.inverse_transform(future_price)
            future_price = future_price.reshape(-1 ,1)
            future_price=future_price.round(2).tolist()
            
                

            
            past_price= past_price.tolist() + future_price #so I get total_price and date(complete)
            
            past_price = list(map(str, past_price))

            for i in range (1, len(past_price)):
                past_price[i] = past_price[i].replace('[', '').replace(']', '')


            data={
                'labels':','.join(date),
                'default': ','.join(past_price)
            }
        K.clear_session()
        return JsonResponse(data)

@login_required(login_url='login')
def dashboard(request):
    dataFile='rawData/PoultryData.csv'
    modelFile='rawData/lstm-chicken.h5'
    durationVar=0
    forecast=52
    current=260
    
    if request.method=='GET':
            commodity=request.GET.get('commodity')
            duration=request.GET.get('duration')
            datatype=request.GET.get('datatype')
            if commodity=='poultry':
                dataFile='rawData/PoultryData.csv'
                modelFile='rawData/lstm-chicken.h5'
            
            elif commodity=='banana':
                dataFile='rawData/PoultryData.csv'
                modelFile='rawData/lstm-chicken.h5'
            
            elif commodity=='kangkung':
                dataFile='rawData/PoultryData.csv'
                modelFile='rawData/lstm-chicken.h5'
            
            elif commodity=='egg':
                dataFile='rawData/PoultryData.csv'
                modelFile='rawData/lstm-chicken.h5'
            
            elif commodity=="":
                dataFile='rawData/PoultryData.csv'
                modelFile='rawData/lstm-chicken.h5'
            

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
                if durationVar<26:
                    forecast=26
                    current=forecast
                else:
                    forecast=26
                    current=durationVar-forecast

            elif datatype=="forecast1year":
                if durationVar<52:
                    forecast=52
                    current=forecast
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
                'duration':durationVar,
                'forecast':forecast,
                'current':current
            }
            request.session['data']=data
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


