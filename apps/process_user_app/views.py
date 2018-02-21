from __future__ import unicode_literals 
 
from django.shortcuts import render, HttpResponse, redirect 
from django.utils.html import escape
from django.contrib import messages
import bcrypt
from .models import User
 
def login(request):
    return render(request, "process_user_app/index.html") 

def verify_login(request):
    errors = User.objects.login_validator(request.POST)
    goto = '/results/'
    email = request.POST['email']
    password = request.POST['password']

    if len(errors):
        for tag, error in errors.iteritems():
            messages.error(request, error, extra_tags=tag)

        request.session['email'] = request.POST['email']

        goto = '/'
    else:
        exists = User.objects.filter(email = email)
        
        if len(exists):
            user=exists[0]
            hashed=user.password

            if bcrypt.hashpw(password.encode(), hashed.encode()) != hashed.encode():
                errors["login_password"] = "Password does not match password on file."

                for tag, error in errors.iteritems():
                    messages.error(request, error, extra_tags=tag)
                
                request.session['email'] = email

                goto = '/'
            else:
                request.session['user_session']=user.id
                request.session['type'] = "logged in"
        else:
            errors["login_email"] = "User doesn't exists! Use valid email address or register."

            for tag, error in errors.iteritems():
                messages.error(request, error, extra_tags=tag)

            request.session['email'] = email

            goto = '/'

    return redirect(goto) 

def logout(request):
    del request.session['user_session']
    del request.session['type']

    if 'first_name' in request.session:
        del request.session['first_name']

    if 'last_name' in request.session:
        del request.session['last_name']

    if 'email' in request.session:
        del request.session['email']

    return redirect('/')

def register(request): 
    return render(request, "process_user_app/register.html") 

def results(request):
    if 'user_session' in request.session:
        user = User.objects.get(id = request.session['user_session'])
        context = {
            'first_name': user.first_name,
            'full_name': user.first_name + ' ' + user.last_name,
            'email': user.email
        }

        return render(request, "process_user_app/results.html", context )

    else:
        return redirect('/')

def create(request): 
    errors = User.objects.basic_validator(request.POST)
    goto = '/results/'

    if len(errors):
        for tag, error in errors.iteritems():
            messages.error(request, error, extra_tags=tag)

        request.session['first_name'] = request.POST['first_name']
        request.session['last_name'] = request.POST['last_name']
        request.session['email'] = request.POST['email']

        goto = '/register/'
    else:
        
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']

        exists = User.objects.filter(email = email)

        if not len(exists):
            pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

            user = User.objects.create(first_name = first_name, last_name = last_name, email = email, password = pw_hash )
            request.session['user_session']=user.id
            request.session['type'] = "registered"

            try:
                del request.session['first_name']
                del request.session['last_name']
                del request.session['email']
            except:
                pass

        else:
            errors["email"] = "User already exists! Use new email address or login."

            for tag, error in errors.iteritems():
                messages.error(request, error, extra_tags=tag)

            request.session['first_name'] = first_name
            request.session['last_name'] = last_name
            request.session['email'] = email
        
            goto = '/register/'

    return redirect(goto)
