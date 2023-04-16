from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager


# Create your models here.
      

class User(AbstractUser):
    firstname=models.CharField(null=True,max_length=200)
    othername=models.CharField(null=True,max_length=200)
    phone=models.CharField(null=True,max_length=20)
    email=models.EmailField(null=True, unique=True)
    #avatar

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']



class Category (models.Model):
    name=models.CharField(blank=True,null=True, max_length=300)
    def __str__(self):
        return self.name

class Requests(models.Model):
    requester=models.TextField(null=True,blank=True)
    amount=models.TextField(blank=True,null=True)
    gateway=models.TextField(null=True, blank=True)
    project=models.TextField(null=  True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='pending')
    paykey=models.CharField(max_length=6,blank=True,null=True)

    def __str__(self):
        return f'Requester: {self.requester}'
    # , Amount: {self.amount}, Gateway: {self.gateway}, Project: {self.project}, paykey:{self.paykey}'
    

class Campaign(models.Model):
    description=models.TextField(null=True,blank=True)
    category=models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    contributors=models.ManyToManyField(User,blank=True, related_name='campaign_contributors')
    #avatar
    #Youtubelink
    owner= models.OneToOneField(User,blank=True, on_delete=models.SET_NULL, null=True)
    #Reviews
    #Returns
    target=models.TextField(null=True, blank=True)
    total_contributions=models.TextField(null=True, blank=True)
    updated=models.DateTimeField(auto_now=True)
    created=models.DateTimeField(auto_now_add=True)
    name=models.CharField(max_length=200)

    class Meta:
        ordering=['-updated','-created']


    def __str__(self):
        
        return self.name
        
    #class Reviews(models.Model):

class Contributions(models.Model):
    contributor=models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    amount=models.CharField(max_length=10, blank=True, null=True)
    invest_campaign=models.ForeignKey(Campaign, on_delete=models.SET_NULL, null=True)
    method=models.TextField(null=True, blank=True)
    status=models.TextField(null=True,blank=True,default="pending")


    def __str__(self):
        return f"Contributions {self.id}"







