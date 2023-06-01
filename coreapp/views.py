
from django.contrib.auth import authenticate, login as account_login, logout
from django.http import HttpResponse
from django.http.response import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict
import json
from django.core.serializers import serialize
from django.db.models import Q
from django.shortcuts import render,redirect
from rest_framework import serializers
from .models import Campaign,Category,Contributions,Requests,User
from django.db.models import F, FloatField, ExpressionWrapper
from coreapp.serializers import CategoryJSONEncoder,UserJSONEncoder
from .forms import CreateUserForm ,CreateProjectForm
from django.conf import settings
from django.core.mail import send_mail
import calendar
import random
import string
from django.views.decorators.csrf import csrf_exempt
import base64
from datetime import datetime , timedelta
import requests
from django.db.models.functions import Extract
from django.db.models import Sum
from django.contrib.auth.hashers import make_password
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes,force_str
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from .tokens import generate_token
from django.core.serializers import serialize
from rest_framework import serializers
from django.http import JsonResponse


# Create your views here.

def homepage(request):

    campaign_list = Campaign.objects.annotate(
        total_contributions=Sum('contributions__amount')
    ).annotate(
        percentage_contributions=ExpressionWrapper(
            F('total_contributions') / F('target') * 100,
            output_field=FloatField()
        )
    )
    

    #statistics for logged in user
    user=request.user
    if user.is_authenticated:
        userproject=Campaign.objects.filter(owner=user)
        amount=Contributions.objects.filter(invest_campaign__in=userproject, status='paid').aggregate(amount=Sum('amount'))
        backers=Contributions.objects.filter(status='paid',invest_campaign__in=userproject).count()
        amount=amount['amount']
        total_investment = Contributions.objects.filter(contributor=user)
        total_sum = 0
        for investment in total_investment:
            amount = investment.amount.replace(',', '') # remove commas
            total_sum += float(amount)
        total_count=total_investment.count()  

        completerequests=Requests.objects.filter(requester=user, status='used')
        completetotal=completerequests.count()                 
        context={'campaign_list': campaign_list,'total':total_sum,'count':
                 total_count,'completerequests':completetotal,'backers':backers,'amount':amount}
    else:
        context = {'campaign_list': campaign_list}
    
    return render(request,'index.html',context)


# def login(request):
#     return render(request, 'login.html')

def login(request):
    next = request.GET.get('next')
    context={
        'next': next
    }
    
    return render(request, 'login.html', context)

def checkmail(request):
    username = request.POST.get('username')
    data = {
        'is_taken': User.objects.filter(email=username).exists(),'username': username
    }
    if data['is_taken']:
        data['error_message'] = 'A user with this username already exists.'
    print(data)    
    return JsonResponse(data)

def accountlogin(request):
    if request.user.is_authenticated:
        #return redirect('home')
        print('authenticated')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        next=request.POST.get('next')
        print(next)

        user=User.objects.get(email=username)
        user = authenticate(request, email=username, password=password)
        print(user)
        if user is not None:
            data = {'success': True,'next':next}
            account_login(request,user)
        else:
            data = {'success': False}
        return JsonResponse(data)


def generate_random_code(length):
    # Define the characters that can be used in the random code
    characters = string.ascii_uppercase + string.digits
    # Generate a random code by randomly selecting characters from the defined set
    code = ''.join(random.choice(characters) for _ in range(length))
    return code

# Example usage: Generate a random code of length 6
random_code = generate_random_code(6)




def logoutuser(request):
    logout(request)
    return redirect('home')

def projectdetails(request, pk):
    project=Campaign.objects.get(id=pk)
    if request.method == 'POST':
        user=request.user
        if user.is_authenticated:
            request_obj=Requests()
            amount=request.POST['amount']
            gateway=request.POST.get('radio-group2')
            requester=request.user
            projectid=project.id
            # print('amount is ' + amount +'project is '+project.name+ 'gateway is' +gateway)
            # print(requester.email)
            paykey=random_code
            request_obj.amount=amount
            request_obj.paykey=paykey
            request_obj.gateway=gateway
            request_obj.requester=requester
            request_obj.project=projectid
            existing_request = Requests.objects.filter(requester=requester, status='pending').first()
            if existing_request:
                print('you have a pending request')
                
                
            else:
                try:    
                        print(amount,gateway,paykey,project,requester)
                        request_obj.save()
                        # server='https://fouth-year-project-production.up.railway.app/payment/'+paykey
                        currentsite = get_current_site(request)
                        newsite='http://'+str(currentsite) +"/"+'payment'+"/"+str(paykey)
                        print(newsite)

                        #send mail to the requester and save to database
                        subject = 'Approval of purchase'
                        message =  f'Dear {requester.first_name} \n We have received and approved your request to purchase equities worthy KES 10,000 for company Z first seeding as at this date {project.created} through mpesa. Please click this link to proceed and make a payment\n once you make the payment, A receipt with order details and confirmation of purchase will be shared to this mail. Please save this mail for future reference\n {newsite}'
                        from_email = settings.EMAIL_HOST_USER
                        recipient_list = [requester]  # Replace with the recipient email address

                        send=send_mail(subject, message, from_email, recipient_list, fail_silently=False)
                        if send==1:
                            print('send successfully')
                        else:
                            print(send)    
                        print('saved')

                        print(message)
                except Exception as e:
                        print("Error saving data: ", str(e))
        else:
            login_next_url = reverse('project', kwargs={'pk': pk})
            login_url = reverse('login') + '?next=' + login_next_url
            return redirect(login_url)
            
                
 
     

    #if request.is_ajax():
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        project = Campaign.objects.select_related('owner').get(id=pk)
        contributions = project.contributions_set.all()
            #projectpercentage=(project.total_contributions/project.target)*100
            #
        target=int(project.target)
        total=Contributions.objects.filter(invest_campaign=pk).aggregate(total_amount=Sum('amount'))
        total=int(total['total_amount'])
        #total=int(project.total_contributions)
        togo=(target)-(total)
        percentage=(total)/(target)*100
        percentage_collected=abs(percentage)
        if percentage_collected<= 0.09:
            percentage_collected=0    

        data={'target':target,'total':total,'togo':togo,'percentage':percentage_collected,'projecttile':project.name,
                'description':project.description,
                'created':project.created,'updated':project.updated, 'category':project.category.name,
                'owner':project.owner.email}

        
        
            # context = {'project': project, 'contributions': contributions, 'percentage_collected': percentage_collected,'togo':togo}
            #return render(request, 'campaign-details.html', data)
        
       # print(data)
        return JsonResponse(data,  encoder=CategoryJSONEncoder)
    
    return render(request,'project.html')

def payment(request,pk):
   paymentdetails=Requests.objects.get(paykey=pk)
   context={'paymentdetails':paymentdetails}  
   return render(request,'payment.html',context)

def pay(request):
    if request.method=='POST':
        amount=request.POST.get('amount')
        user=request.POST.get('user')
        gateway=request.POST.get('gateway')
        paykey=request.POST.get('paykey')
        project=request.POST.get('project')
        phone=request.POST.get('phone')

        if phone.startswith('07'):
            #drop the first zero of the number
            phone=phone[1:]
            phone= "254"+phone
        elif phone.startswith('254'):
            pass
        Contributions_obj=Contributions()
        campaign_instance = Campaign.objects.get(id=project)
        user_instance = User.objects.get(email=user)
        Contributions_obj.invest_campaign=campaign_instance
        Contributions_obj.contributor=user_instance
        Contributions_obj.amount=amount
        Contributions_obj.method=gateway
        request_status = Requests.objects.get(paykey=paykey)

        campaign_details=Campaign.objects.get(id=project)
        expected=float(amount)*0.01*float(campaign_details.roi)
        print("expected" +str(expected))

        Contributions_obj.expected=expected
        Contributions_obj.status='paid'

        
        print(request_status.status)
        try:
            # consumer_secret = "fgO9yRGp0GPppQ9W"
            # consumer_key = "hN5lYtXcq9l0bv4NsuMlMQ5Q8UTI9Tyv"


            # api_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
            # r = requests.get(api_URL, auth=(consumer_key,consumer_secret))
            # mpesa_access_token = json.loads(r.text)
            # validated_mpesa_access_token = mpesa_access_token['access_token']
            # print(validated_mpesa_access_token)

            # headers = {
            #     'Content-Type': 'application/json',
            #     'Authorization': "Bearer " + validated_mpesa_access_token
            # }

            # shortcode = '174379'
            # formated_datetime = datetime.now().strftime("%Y%m%d%H%M%S")  # Formats the datetime i a format the safaricom expects
            # passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'

            # validator = shortcode + passkey + formated_datetime
            # password = base64.b64encode(validator.encode()).decode('ascii')
            # print(password)
            # payload = {
            #     "BusinessShortCode": shortcode,
            #     "Password": password,
            #     "Timestamp": formated_datetime,
            #     "TransactionType": "CustomerPayBillOnline",
            #     "Amount": "1",  #amount needs to be string
            #     "PartyA": phone, #partyA, PartyB and PhoneNumber should be in string
            #     "PartyB": shortcode,
            #     "PhoneNumber": phone,
            #     "InitiatorName":"testapi",
            #     "InitiatorPassword":"Safaricom999!*!",
            #     "CallBackURL": 'https://fouth-year-project-production.up.railway.app/callback/',
            #     "AccountReference": "CompanyXLTD",
            #     "TransactionDesc": "Payment of X"
            # }
            # print(payload)
            # response = requests.post('https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest',
            #                           headers=headers, json=payload)
            # print(response.text)

            # code=json.loads(response.text)
            # #Rescode = code['ResponseCode']
           
            # checkoutid= code['CheckoutRequestID']
            # Contributions_obj.checkoutid=checkoutid

            # print(Contributions_obj.checkoutid)

            Contributions_obj.save()
            
                    
        except Exception as e:
            print("couldn't save" +str(e))
        # print(amount,gateway,paykey,project,user,phone, "being saved: "+ int(Contributions_obj.invest_campaign))

    return render(request,'payment.html')


@csrf_exempt
def callback(request): 
    
    print(request)
    print(request.body)


    return HttpResponse("here")


def userrequests(request):
    user=request.user
    if user.is_authenticated:
        requests = Requests.objects.filter(requester=user)
        pending= Requests.objects.filter(requester=user, status='pending')
        total_pending=pending.count()

        complete= Requests.objects.filter(requester=user, status='used')
        total_complete=complete.count()

        context={'requests':requests,'total_pending':total_pending, 'total_complete':total_complete}

    return render(request,'requests.html',context)


def userpurchases(request):
    user = request.user
    if user.is_authenticated:
        purchases=Contributions.objects.filter(contributor=user, status='paid')
    
        context={'purchases':purchases}

        return render(request, 'userpurchases.html',context)
    


def report(request):
    # if request.is_ajax():
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        user = request.user
        usermonthly = Contributions.objects.exclude(status='pending').filter(contributor=user).annotate(
            month=Extract('created_at','month')).values('contributor','month').annotate(
            total=Sum('amount'))
        
        campaign_totals = Campaign.objects.annotate(totalamount=
                                                    Sum('contributions__amount', 
                                                        filter=Q(contributions__contributor=user,contributions__status='paid'))).values('name', 
                                                                                                           'totalamount')
        

        paidorders=Contributions.objects.filter(contributor=user,status='paid').count()
        pendingorders=Contributions.objects.filter(contributor=user,status='pending').count()
        ordersdata={'paid':paidorders, 'pending': pendingorders}
        print(ordersdata)
        totalsdata = []
        for campaign in campaign_totals:
            campaign_data = {'name': campaign['name'], 'total_contributions': campaign['totalamount']}
            totalsdata.append(campaign_data)
        

        data = []
        for contribution in usermonthly:
            month = contribution['month']
            month_name = calendar.month_name[month]
            contribution['month_name'] = month_name

            total = contribution['total']
            contribution_data = {'month_name': month_name, 'total': total}
            data.append(contribution_data)

        #print(totalsdata)   
        data={'data': data, 'totalsdata':totalsdata,'ordersdata': ordersdata}
        return JsonResponse(data, safe=False)

    else:
       return render(request,'report.html')
   
        
def register(request):
     
    form =CreateUserForm()
    context={'form':form}

    return render(request, 'register.html', context)

class RegistrationForm(forms.Form):
    username = forms.CharField()
    first_name = forms.CharField()
    last_name = forms.CharField()
    user_type = forms.CharField()
    pass1 = forms.CharField()
    pass2 = forms.CharField()



def registeraccount(request):
   regresponse = None
   if request.method=='POST':
       form_data = request.POST.copy()  # Create a mutable copy of the request.POST data
       form = RegistrationForm(form_data)
       if form.is_valid():
            username = form.cleaned_data['username']
            firstname = form.cleaned_data['first_name']
            lastname = form.cleaned_data['last_name']
            usertype = form.cleaned_data['user_type']
            pass1 = form.cleaned_data['pass1']
            pass2 = form.cleaned_data['pass2']
            if pass1!=pass2:
                regresponse='passwords do not match'
            else:
                myuser=User.objects.create_user(username=username)
                myuser.first_name=firstname
                myuser.last_name=lastname
                myuser.set_password(pass1)
                myuser.type=usertype
                myuser.email=username
                myuser.is_active=False
                myuser.save()
                regresponse='Account successfully registered. please check your mail and proceed to activate account'
                
                #send email address to verify account
                currentsite = get_current_site(request)
                subject = 'mail confirmation @ The online SME crowdfunding system'
                message2 =  render_to_string('email_confirmation.html',{
                    'name': myuser.first_name,
                    'domain':currentsite.domain,
                    'uid': base64.urlsafe_b64encode(force_bytes(myuser.pk)).decode('utf-8'),
                    'token': generate_token.make_token(myuser)
                })
                from_email = settings.EMAIL_HOST_USER
                recipient = [myuser.email] # Replace with the recipient email address

                send_mail(subject, message2, from_email, recipient, fail_silently=False)
                print(message2)

                #print(currentsite)
            
                           
       else:
           errors = form.errors.as_json()
           print(errors)
   return JsonResponse(regresponse, safe=False) 


def activate(request, uidb64,token):
   try:
        uid=force_str(urlsafe_base64_decode(uidb64))
        myuser=User.objects.get(pk=uid)

   except (TypeError, ValueError,OverflowError, User.DoesNotExist):
       myuser=None

   if myuser is not None and generate_token.check_token(myuser,token):
        myuser.is_active=True
        myuser.save()
        account_login(request,myuser)
        return redirect('home')
   else:
        return render(request,'activationfailed.html')
   
def get_weekly_contributions_sum(user):
    # Retrieve the campaign owned by the logged-in user
    campaign = Campaign.objects.filter(owner=user).first()

    # If the campaign exists, calculate the sum of contributions for each week
    if campaign:
        # Get the campaign creation date
        campaign_start_date = campaign.created.date()

        # Get the current date
        today = datetime.now().date()

        # Calculate the start date for the desired number of weeks ago
        start_date = campaign_start_date - timedelta()

        # Initialize a list to store dictionaries for weekly sums
        weekly_sums = []

        # Iterate over the past weeks, starting from the start date
        while start_date <= today:
            # Calculate the end date for the current week
            end_date = start_date + timedelta(days=6)

            # Calculate the sum of contributions within the current week
            contributions_sum = Contributions.objects.filter(
                invest_campaign=campaign,
                created_at__date__gte=start_date,
                created_at__date__lte=end_date
            ).aggregate(total_amount=Sum('amount'))['total_amount']

            # Determine the week name and format the week range
            if start_date <= today <= end_date:
                week_range = 'This Week'
            elif start_date <= campaign_start_date <= end_date:
                week_range = 'Campaign Start Week'
            elif start_date > today - timedelta(days=7):
                week_range = 'Previous Week'
            else:
                week_range = f"Week of {start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}"

            # Create a dictionary with 'week' and 'amount' keys
            weekly_dict = {'week': week_range, 'amount': contributions_sum or 0}

            # Add the weekly dictionary to the list
            weekly_sums.append(weekly_dict)

            start_date += timedelta(weeks=1)

        return weekly_sums
    else:
        return {}




class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = '__all__'

def myproject(request):
    context={}
    user = request.user
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':    
        userprojects = Campaign.objects.filter(owner=user)
        if userprojects.exists():
            project_data = []
            for project in userprojects:
                total = project.contributions_set.filter(status='paid').aggregate(total=Sum('amount'))['total'] or 0
                totalbackers = project.contributions_set.filter(status='paid').count()
                deficit = int(project.target) - int(total)

                percentage = (int(total) / int(project.target)) * 100
                percentage=round(percentage,2)
                pendingorders = project.contributions_set.filter(status='pending').count()
                paidorders = project.contributions_set.filter(status='paid').count()
                totals={'total':total,'totalbackers':totalbackers,'deficit':deficit,'percentage':percentage}
                orders={'pending': pendingorders ,'paid': paidorders}

                weekly_sums = get_weekly_contributions_sum(user)

                project_dict = {
                    'totals': totals,
                    'project': CampaignSerializer(project).data,
                    'percentage': percentage,
                    'orders':orders,
                    'weekly': weekly_sums,
                    
                }

                project_data.append(project_dict)
                totals=project_data[0]['totals']
                return JsonResponse(project_data, safe=False)
        else:
            project_data='0'
            # return JsonResponse({'message': 'No projects found for the user'}, status=200)
            return JsonResponse(project_data, safe=False)
            
    else:  
        form =CreateProjectForm()
        context={'form':form}
        form = CreateProjectForm()
        form = CreateProjectForm()
        if request.method == 'POST':
            form=CreateProjectForm(request.POST)
            if form.is_valid():
                submission = form.save(commit=False)
                submission.owner=request.user
                submission.save()

            else:
                print('invalid')  
        else:
           print('ivalid request')
        return render(request, 'myproject.html',context)

def payables(request):
    user=request.user
    project=Campaign.objects.filter(owner=user)
    purchases=Contributions.objects.filter(invest_campaign__in=project, status='paid',paidout=False).exclude(expected=0)
    total=purchases.aggregate(total=Sum('expected'))

    total=(total['total'])

    context={'purchases':purchases, 'total':total}


    return render(request, 'payables.html',context)      


    
           


        
    




