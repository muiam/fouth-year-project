
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
from .models import Campaign,Category,User,Contributions,Requests
from django.db.models import F, FloatField, ExpressionWrapper
from coreapp.serializers import CategoryJSONEncoder,UserJSONEncoder
from .forms import ContributionForm
from django.conf import settings
from django.core.mail import send_mail
import random
import string
from django.views.decorators.csrf import csrf_exempt
import base64
from datetime import datetime
import requests



# Create your views here.

def homepage(request):
    campaign_list=Campaign.objects.annotate(
        percentage_contributions=ExpressionWrapper(
            F('total_contributions') / F('target') * 100,
            output_field=FloatField()
        ))
    

    #statistics for logged in user
    user=request.user
    if user.is_authenticated:
        total_investment = Contributions.objects.filter(contributor=user)
        total_sum = 0
        for investment in total_investment:
            amount = investment.amount.replace(',', '') # remove commas
            total_sum += float(amount)
        total_count=total_investment.count()  

        completerequests=Requests.objects.filter(requester=user, status='used')
        completetotal=completerequests.count()                 
        context={'campaign_list': campaign_list,'total':total_sum,'count':total_count,'completerequests':completetotal}
    else:
        context = {'campaign_list': campaign_list}
    
    return render(request,'index.html',context)


def login(request):
    return render(request, 'login.html')

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

        user=User.objects.get(email=username)
        user = authenticate(request, email=username, password=password)
        print(user)
        if user is not None:
            account_login(request,user)
            data = {'success': True}
        else:
            data = {'success': False}
        print(data)
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


# def projectdetails(request,pk):
#     project=Campaign.objects.get(id=pk)
#     contributions=project.contributions_set.all()
#     context={'project':project, 'contributions':contributions}
#     return render(request,'campaign-details.html', context)

def projectdetails(request, pk):
    project=Campaign.objects.get(id=pk)
    if request.method == 'POST':
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
                    server='https://fouth-year-project-production.up.railway.app/payment/'+paykey

                    #send mail to the requester and save to database
                    subject = 'Approval of purchase'
                    message =  f'Dear {requester.firstname} \n We have received and approved your request to purchase equities worthy x for company {project.name} as at this date {project.created} through mpesa. Please click this link to proceed and make a payment\n once you make the payment, A receipt with order details and confirmation of purchase will be shared to this mail. Please save this mail for future reference\n {server}'
                    from_email = settings.EMAIL_HOST_USER
                    recipient_list = ['mwendwaharry01@gmail.com']  # Replace with the recipient email address

                    send=send_mail(subject, message, from_email, recipient_list, fail_silently=False)
                    if send==1:
                        print('send successfully')
                    else:
                        print(send)    
                    print('saved')

                    print(message)
            except Exception as e:
                    print("Error saving data: ", str(e))
            

            
                
 
     

    # if request.is_ajax():
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        project = Campaign.objects.select_related('owner').get(id=pk)
        contributions = project.contributions_set.all()
            #projectpercentage=(project.total_contributions/project.target)*100
            #
        target=int(project.target)
        total=int(project.total_contributions)
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

        
        print(request_status.status)
        try:
            consumer_secret = "fgO9yRGp0GPppQ9W"
            consumer_key = "hN5lYtXcq9l0bv4NsuMlMQ5Q8UTI9Tyv"


            api_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
            r = requests.get(api_URL, auth=(consumer_key,consumer_secret))
            mpesa_access_token = json.loads(r.text)
            validated_mpesa_access_token = mpesa_access_token['access_token']
            print(validated_mpesa_access_token)

            headers = {
                'Content-Type': 'application/json',
                'Authorization': "Bearer " + validated_mpesa_access_token
            }

            shortcode = '174379'
            formated_datetime = datetime.now().strftime("%Y%m%d%H%M%S")  # Formats the datetime i a format the safaricom expects
            passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'

            validator = shortcode + passkey + formated_datetime
            password = base64.b64encode(validator.encode()).decode('ascii')
            print(password)
            payload = {
                "BusinessShortCode": shortcode,
                "Password": password,
                "Timestamp": formated_datetime,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": "1",  #amount needs to be string
                "PartyA": phone, #partyA, PartyB and PhoneNumber should be in string
                "PartyB": shortcode,
                "PhoneNumber": phone,
                # "InitiatorName":"testapi",
                # "InitiatorPassword":"Safaricom999!*!",
                "CallBackURL": 'https://fouth-year-project-production.up.railway.app/callback/',
                "AccountReference": "CompanyXLTD",
                "TransactionDesc": "Payment of X"
            }
            print(payload)
            response = requests.post('https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest',
                                      headers=headers, json=payload)
            print(response.text)

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
        purchases=Contributions.objects.filter(contributor=user).exclude(status='pending')
    
        context={'purchases':purchases}

        return render(request, 'userpurchases.html',context)
    




