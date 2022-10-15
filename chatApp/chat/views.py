import json
from django.contrib import messages
from django.contrib.auth import authenticate
from urllib import response
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, auth
from django.shortcuts import redirect, render
import datetime
from .models import *
import pickle
import os
from nltk.stem import PorterStemmer
from django.contrib import messages

# Create your views here.
# from chat.models import Thread
models_path = os.path.join(os.getcwd(), 'chat/Algorithm')
tv = pickle.load(open(os.path.join(models_path, 'CountVectorizer.pkl'), 'rb'))
model = pickle.load(open(os.path.join(models_path, 'spam_classifier.pkl'), 'rb'))

# @login_required(login_url = "")
def messages_page(request):
    
    # if request.method=="POST":
    #     user = request.user
    #     persons=request.POST['persons']
    #     timS = datetime.datetime.now()
    #     second_person = User.objects.get(username = persons)
    #     print(persons)
    #     print(second_person)
    #     result = Thread(first_person=user,second_person=second_person,updated=timS,timestamp=timS)
    #     result.save()
    # mess = ChatMessage.objects.filter(user_id = request.user).order_by('-id').values('message')[0]
    th = Thread.objects.by_user(user=request.user).prefetch_related('chatmessage_thread').order_by('timestamp').values()

    print("the thread set is--")
    print(th)
    thr = Thread.objects.by_user(user=request.user).prefetch_related('chatmessage_thread').order_by('timestamp').values("second_person_id")[0]['second_person_id'] 
       
    print("the second_person_id is--")
    print(thr)

    mess = ChatMessage.objects.filter(user_id = thr).order_by('-id').values('message')[0]
    mess1 = ChatMessage.objects.filter(user_id = thr).order_by('-id').values()[0]

    print("the fetched message is---")
    print(mess1)
    
    currUser = request.user
    print("Current User Name--")
    print(currUser.id)
    
    demomesaage = mess.get('message')
    print("Message--")
    print(demomesaage)
    message = demomesaage
    
    message = ' '.join([PorterStemmer().stem(word) for word in message.split()])
       
    message = tv.transform([message]).toarray()
    
    message = message[0].reshape((1,-1))
    
    abc = model.predict(message)
    print(abc)
    if model.predict(message):
             
        print("Spam message form views")       
        messages.error(request, "It's  a SPAM Message.")
        
    else:
        print("Not Spam message form views")
        messages.success(request, "It's not a SPAM Message.")  
        
    threads = Thread.objects.by_user(user=request.user).prefetch_related('chatmessage_thread').order_by('timestamp')
    print(threads)
    chatwith = User.objects.all()
    context = {
        'Threads':threads,
        'Friends':chatwith
    }
    return render(request, 'messages.html',context)

def register(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1==password2:
            if User.objects.filter(username=username).exists():
                messages.info(request,'Username Taken')
                return redirect("/register")
            elif User.objects.filter(email=email).exists():
                messages.info(request,'Email Taken')
                return redirect("/register")
            else:
               user = User.objects.create_user(username=username,password=password1,email=email,first_name=first_name,last_name=last_name)
               user.save()
               print("user created") 
               return redirect("/")
        else:
            print('Password not matching')
            return redirect("/register")
    else:
        return render(request,'register.html')


def login(request):
    if request.method=='POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request,username=username, password=password)

        if user is not None and user.is_active:
            auth.login(request,user)
            # messages.success(request,"Authentication Successfull")
            return redirect("ChatHome")
        else:
            # messages.error(request,"Authentication Error")
            return redirect("login")
    # No backend authenticated the credentials
        # if not user:
        #     messages.info(request,'Invalid Credentials')
        #     print("User not authenticated")
        #     return render(request,'login.html')
          
        # else:
          
    else: 
        print("From main else")   
    return render(request,'login.html')

def logout(request):
    auth.logout(request)
    return redirect('/')