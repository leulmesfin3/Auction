from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
# Create your views here.


def route(request):
    if request.user.is_authenticated:
        return redirect('/home')
    return redirect('/login')


def mdPage(request):
    return render(request, 'md.html')

def loginPage(request):
    message_danger = None
    username = None
    if request.user.is_authenticated:
        return redirect("route")
    elif request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            if not remember_me:
                request.session.set_expiry(0)
            if request.GET.get('next'):
                return redirect(request.GET.get('next'))
            return redirect('route')
        else:
            message_danger = "Invalid Username or Password"
    return render(request, 'login.html', {"message_danger":message_danger,
                                          "username":username if username else ""})


def logoutPage(request):
    logout(request)
    return redirect('/login')


@login_required(login_url="/login/")
def homePage(request):
    return render(request, 'home.html')

@login_required(login_url="/login/")
def viewLotPage(request):
    return render(request, 'viewLot.html')
