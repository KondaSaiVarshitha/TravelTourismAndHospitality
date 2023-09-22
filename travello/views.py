from django.shortcuts import render
from .models import Destination
from .models import Detailed_desc
from .models import passenger_detail
from .models import Cards
from .models import Transactions
from .models import NetBanking
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth.decorators import *
from django.utils.dateparse import parse_date
from django.views.decorators.cache import cache_control
from django.core.mail import send_mail
from django import forms
from django.forms.formsets import formset_factory
from django.shortcuts import render
from django.template import Library
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.core.mail import send_mail, BadHeaderError
import pandas as pd
import numpy as np

import random


#  __lte=      is eqivelent to lessthan or euivelent
#    table.all().filter().exclude().filer()   for two filters and one excluding condition
# Create your views here.

def index(request):
    dests = Destination.objects.all()
    dest1 = []
    j = 0
    for i in range(6):
        j = j + 2
        temp = Detailed_desc.objects.get(dest_id=j)
        dest1.append(temp)

    return render(request, 'index.html', {'dests': dests, 'dest1': dest1})


def about(request):
    return render(request, 'about.html')


def register(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.info(request, 'Username Taken')
                return redirect('register')
            elif User.objects.filter(email=email).exists():
                messages.info(request, 'Email already Taken')
                return redirect('register')
            else:
                user = User.objects.create_user(username=username, password=password1, email=email, last_name=last_name,
                                                first_name=first_name)
                user.save()
                print('user Created')
                return redirect('login')
        else:
            messages.info(request, 'Password is not matching ')
            return redirect('register')
        return redirect('index')
    else:
        return render(request, 'register.html')


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            messages.info(request, 'Sucessfully Logged in')
            email = request.user.email
            print(email)
            content = 'Hello ' + request.user.first_name + ' ' + request.user.last_name + '\n' + 'You are logged in in our site.keep connected and keep travelling.'
            # send_mail('Alert for Login', content
            #           , 'travellotours89@gmail.com', [email], fail_silently=True)
            dests = Destination.objects.all()
            return render(request, 'index.html', {'dests': dests})
        else:
            messages.info(request, 'Invalid credential')
            return redirect('login')
    else:
        return render(request, 'login.html')


def logout(request):
    auth.logout(request)
    return redirect('index')


@login_required(login_url='login')
def destination_list(request, city_name):
    dests = Detailed_desc.objects.all().filter(country=city_name)
    return render(request, 'travel_destination.html', {'dests': dests})


def destination_details(request, city_name):
    dest = Detailed_desc.objects.get(dest_name=city_name)
    price = dest.price
    request.session['price'] = price
    request.session['city'] = city_name
    return render(request, 'destination_details.html', {'dest': dest})


def search(request):
    try:
        place1 = request.session.get('place')
        print(place1)
        dest = Detailed_desc.objects.get(dest_name=place1)
        print(place1)
        return render(request, 'destination_details.html', {'dest': dest})
    except:
        messages.info(request, 'Place not found')
        return redirect('index')


class KeyValueForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    age = forms.IntegerField()


def pessanger_detail_def(request, city_name):
    KeyValueFormSet = formset_factory(KeyValueForm, extra=1)
    if request.method == 'POST':
        formset = KeyValueFormSet(request.POST)
        if formset.is_valid():
            temp_date = datetime.strptime(request.POST['trip_date'], "%Y-%m-%d").date()
            date1 = datetime.now().date()
            if temp_date < date1:
                return redirect('index')
            obj = passenger_detail.objects.get(Trip_id=3)
            pipo_id = obj.Trip_same_id
            # pipo_id =4
            request.session['Trip_same_id'] = pipo_id
            price = request.session['price']
            city = request.session['city']
            print(request.POST['trip_date'])
            # temp_date = parse_date(request.POST['trip_date'])
            temp_date = datetime.strptime(request.POST['trip_date'], "%Y-%m-%d").date()
            usernameget = request.user.get_username()
            print(temp_date)
            request.session['n'] = formset.total_form_count()
            for i in range(0, formset.total_form_count()):
                form = formset.forms[i]

                t = passenger_detail(Trip_same_id=pipo_id, first_name=form.cleaned_data['first_name'],
                                     last_name=form.cleaned_data['last_name'],
                                     age=form.cleaned_data['age'],
                                     Trip_date=temp_date, payment=price, username=usernameget, city=city)
                t.save()
                # print (formset.forms[i].form-[i]-value)

            obj.Trip_same_id = (pipo_id + 1)
            obj.save()
            no_of_person = formset.total_form_count()
            price1 = no_of_person * price
            GST = price1 * 0.18
            GST = float("{:.2f}".format(GST))
            final_total = GST + price1
            request.session['pay_amount'] = final_total
            return render(request, 'payment.html', {'no_of_person': no_of_person,
                                                    'price1': price1, 'GST': GST, 'final_total': final_total,
                                                    'city': city})
    else:
        formset = KeyValueFormSet()

        return render(request, 'sample.html', {'formset': formset, 'city_name': city_name, })


def upcoming_trips(request):
    username = request.user.get_username()
    date1 = datetime.now().date()
    person = passenger_detail.objects.all().filter(username=username).filter(pay_done=1)
    person = person.filter(Trip_date__gte=date1)
    print(date1)
    return render(request, 'upcoming trip1.html', {'person': person})


@login_required(login_url='login')
def card_payment(request):
    card_no = request.POST.get('card_number')
    pay_method = 'Debit card'
    MM = request.POST['MM']
    YY = request.POST['YY']
    CVV = request.POST['cvv']

    request.session['dcard'] = card_no
    balance = Cards.objects.get(Card_number=card_no, Ex_month=MM, Ex_Year=YY, CVV=CVV).Balance
    request.session['total_balance'] = balance
    mail1 = Cards.objects.get(Card_number=card_no, Ex_month=MM, Ex_Year=YY, CVV=CVV).email

    if int(balance) >= int(request.session['pay_amount']):
        # print("if ma gayu")
        rno = random.randint(100000, 999999)
        request.session['OTP'] = rno

        amt = request.session['pay_amount']
        username = request.user.get_username()
        print(username)
        user = User.objects.get(username=username)
        mail_id = user.email
        print([mail_id])
        msg = 'Your OTP For Payment of ₹' + str(amt) + ' is ' + str(rno)
        # print(msg)
        # print([mail_id])
        # print(amt)
        send_mail('OTP for Debit card Payment',
                  msg,
                  'yashwanthm1582@gmail.com',
                  [mail_id],
                  fail_silently=False)
        return render(request, 'OTP.html')
    return render(request, 'wrongdata.html')


@login_required(login_url='login')
def net_payment(request):
    username = request.POST['cardNumber']
    Password1 = request.POST['pass']
    Bank_name = request.POST['banks']
    usernameget = request.user.get_username()
    Trip_same_id1 = request.session['Trip_same_id']
    amt = int(request.session['pay_amount'])
    pay_method = 'Net Banking'
    try:
        r = NetBanking.objects.get(Username=username, Password=Password1, Bank=Bank_name)
        balance = r.Balance
        request.session['total_balance'] = balance
        if int(balance) >= int(request.session['pay_amount']):
            total_balance = int(request.session['total_balance'])
            rem_balance = int(total_balance - int(request.session["pay_amount"]))
            r.Balance = rem_balance
            r.save(update_fields=['Balance'])
            r.save()
            t = Transactions(username=usernameget, Trip_same_id=Trip_same_id1, Amount=amt, Payment_method=pay_method,
                             Status='Successfull')
            t.save()
            return render(request, 'confirmetion_page.html')
        else:
            t = Transactions(username=usernameget, Trip_same_id=Trip_same_id1, Amount=amt, Payment_method=pay_method)
            t.save()
            return render(request, 'wrongdata.html')
    except:
        return render(request, 'wrongdata.html')


@login_required(login_url='login')
def otp_verification(request):
    otp1 = int(request.POST['otp'])
    usernameget = request.user.get_username()
    Trip_same_id1 = request.session['Trip_same_id']
    amt = int(request.session['pay_amount'])
    pay_method = 'Debit card'
    if otp1 == int(request.session['OTP']):
        del request.session["OTP"]
        total_balance = int(request.session['total_balance'])
        rem_balance = int(total_balance - int(request.session["pay_amount"]))
        c = Cards.objects.get(Card_number=request.session['dcard'])
        c.Balance = rem_balance
        c.save(update_fields=['Balance'])
        c.save()
        t = Transactions(username=usernameget, Trip_same_id=Trip_same_id1, Amount=amt, Payment_method=pay_method,
                         Status='Successfull')
        t.save()
        z = passenger_detail.objects.all().filter(Trip_same_id=Trip_same_id1)
        for obj in z:
            obj.pay_done = 1
            obj.save(update_fields=['pay_done'])
            obj.save()
            print(obj.pay_done)
        return render(request, 'confirmetion_page.html')
    else:
        t = Transactions(username=usernameget, Trip_same_id=Trip_same_id1, Amount=amt, Payment_method=pay_method)
        t.save()
        return render(request, 'wrong_OTP.html')


@login_required(login_url='login')
def data_fetch(request):
    username = request.user.get_username()
    person = passenger_detail.objects.all().filter(username=username)


df3 = pd.read_json(
    'https://cdn.jsdelivr.net/gh/highcharts/highcharts@v7.0.0/samples/data/world-population-density.json')


def indexpage(request):
    confirmedGlobal = pd.read_csv(
        'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data'
        '/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv',
        encoding='utf-8', na_values=None)
    # deathGLobal=pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv')
    # recoverGlobal=pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv')
    uniqueCountryNames = pd.unique(confirmedGlobal['Country/Region'])
    contryNames, countsVal, logVals, overallCount, dataForMapGraph, maxVal = getBarData(confirmedGlobal,
                                                                                        uniqueCountryNames)
    dataForheatMap, dateCat = getHeatMapData(confirmedGlobal, contryNames)
    datasetForLine, axisvalues = getLinebarGroupData(confirmedGlobal, uniqueCountryNames)
    context = {'dateCat': dateCat, 'dataForheatMap': dataForheatMap, 'maxVal': maxVal,
               'dataForMapGraph': dataForMapGraph, 'axisvalues': axisvalues, 'datasetForLine': datasetForLine,
               'uniqueCountryNames': uniqueCountryNames, 'contryNames': contryNames, 'countsVal': countsVal,
               'logVals': logVals, 'overallCount': overallCount}
    return render(request, 'datahist.html', context)


def getBarData(confirmedGlobal, uniqueCountryNames):
    df2 = confirmedGlobal[list(confirmedGlobal.columns[1:2]) + list([confirmedGlobal.columns[-2]])]
    df2.columns = ['Country/Region', 'values']
    df2 = df2.sort_values(by='values', ascending=False)
    contryNames = list(df2['Country/Region'].values)
    countsVal = list(df2['values'].values)
    maxVal = max(countsVal)
    overallCount = sum(countsVal)
    logVals = list(np.log(ind) if ind != 0 else 0 for ind in countsVal)
    dataForMapGraph = getDataforMap(uniqueCountryNames, df2)
    # dictVal=[]
    # for i in range(df2.shape[0]):
    #     dictVal.append(dict(df2.ix[i]))
    return contryNames, countsVal, logVals, overallCount, dataForMapGraph, maxVal


def getLinebarGroupData(confirmedGlobal, uniqueCountryNames):
    colNames = confirmedGlobal.columns[4:-1]
    datasetsForLine = []
    for i in uniqueCountryNames:
        temp = {'label': i, 'fill': 'false',
                'data': confirmedGlobal[confirmedGlobal['Country/Region'] == i][colNames].sum().values.tolist()}
        datasetsForLine.append(temp)
    return datasetsForLine, list(range(len(colNames)))


def getDataforMap(uniqueCOuntryName, df2):
    dataForMap = []
    for i in uniqueCOuntryName:
        try:
            tempdf = df3[df3['name'] == i]
            temp = {"code3": list(tempdf['code3'].values)[0], "name": i,
                    "value": df2[df2['Country/Region'] == i]['values'].sum(), "code": list(tempdf['code'].values)[0]}
            dataForMap.append(temp)
        except:
            pass
    print(len(dataForMap))
    return dataForMap


def getHeatMapData(confirmedGlobal, contryNames):
    df3 = confirmedGlobal[list(confirmedGlobal.columns[1:2]) + list(list(confirmedGlobal.columns.values)[-6:-1])]
    dataForheatMap = []
    for i in contryNames:
        try:
            tempdf = df3[df3['Country/Region'] == i]
            temp = {"name": i, "data": [{'x': j, 'y': k} for j, k in
                                        zip(tempdf[tempdf.columns[1:]].sum().index,
                                            tempdf[tempdf.columns[1:]].sum().values)]}
            dataForheatMap.append(temp)
        except:
            pass
    dateCat = list(list(confirmedGlobal.columns.values)[-6:-1])
    return dataForheatMap, dateCat


def drillDownACountry(request):
    print(request.POST.dict())
    countryName = request.POST.get('countryName')
    confirmedGlobal = pd.read_csv(
        'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data'
        '/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv',
        encoding='utf-8', na_values=None)
    countryDataSpe = pd.DataFrame(confirmedGlobal[confirmedGlobal['Country/Region'] == countryName][
                                      confirmedGlobal.columns[4:-1]].sum()).reset_index()
    countryDataSpe.columns = ['country', 'values']
    countryDataSpe['lagVal'] = countryDataSpe['values'].shift(1).fillna(0)
    countryDataSpe['incrementVal'] = countryDataSpe['values'] - countryDataSpe['lagVal']
    countryDataSpe['rollingMean'] = countryDataSpe['incrementVal'].rolling(window=4).mean()
    countryDataSpe = countryDataSpe.fillna(0)
    datasetsForLine = [
        {'yAxisID': 'y-axis-1', 'label': 'Daily Travel Data', 'data': countryDataSpe['values'].values.tolist(),
         'borderColor': '#03a9fc', 'backgroundColor': '#03a9fc', 'fill': 'false'},
        {'yAxisID': 'y-axis-2', 'label': 'Rolling Mean 4 days', 'data': countryDataSpe['rollingMean'].values.tolist(),
         'borderColor': '#fc5203', 'backgroundColor': '#fc5203', 'fill': 'false'}]
    axisvalues = countryDataSpe.index.tolist()
    uniqueCountryNames = pd.unique(confirmedGlobal['Country/Region'])
    contryNames, countsVal, logVals, overallCount, dataForMapGraph, maxVal = getBarData(confirmedGlobal,
                                                                                        uniqueCountryNames)
    dataForheatMap, dateCat = getHeatMapData(confirmedGlobal, contryNames)
    context = context = {"countryName": countryName, 'axisvalues': axisvalues, 'datasetsForLine': datasetsForLine,
                         'dateCat': dateCat, 'dataForheatMap': dataForheatMap, 'maxVal': maxVal,
                         'dataForMapGraph': dataForMapGraph, 'uniqueCountryNames': uniqueCountryNames,
                         'contryNames': contryNames, 'countsVal': countsVal, 'logVals': logVals,
                         'overallCount': overallCount}

    return render(request, 'index2.html', context)


def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "password_reset_email.txt"
                    c = {
                        "email": 'travelyaatri26@gmail.com',
                        'domain': '127.0.0.1:8000',
                        'site_name': 'Travel Yaatri',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http',
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_mail(subject, email, 'admin@example.com', [user.email], fail_silently=False)
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    return redirect("/password_reset/done/")
    else:
        password_reset_form = PasswordResetForm()
        return render(request=request, template_name="password_reset.html",
                      context={"password_reset_form": password_reset_form})
