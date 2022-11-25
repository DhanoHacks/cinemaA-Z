"""Stores all views/functions involved in register app
"""
from django.shortcuts import render, redirect
from .forms import RegisterForm

# Create your views here.
def register(response):
    """Renders the registration page for new users
    """
    if response.method == "POST":
        form = RegisterForm(response.POST)   
        if form.is_valid():
            form.save()
            return redirect("/login")
    else:     
        form = RegisterForm()
    return render(response, "register/register.html", {"form":form})

def user(response):
    """Renders the profile page for the user
    """
    if response.method == "POST":
        user = response.user
        user.delete()
        print(user)
        return redirect("/register")
    return render(response, "register/user.html", {})
