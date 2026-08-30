from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect


def login_view(request):

    # If already logged in, don't show login page again
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        remember = request.POST.get("remember")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            if not user.is_active:
                messages.error(
                    request,
                    "Your account has been deactivated. Please contact the administrator."
                )
                return render(
                    request,
                    "accounts/login.html"
                )

            # Create authenticated session
            login(request, user)

            # Remember Me
            if remember:
                # Keep user logged in for 14 days
                request.session.set_expiry(
                    60 * 60 * 24 * 14
                )
            else:
                # Session expires when browser closes
                request.session.set_expiry(0)

            return redirect("home")

        messages.error(
            request,
            "Invalid username or password."
        )

    return render(
        request,
        "accounts/login.html"
    )


@login_required
def logout_view(request):

    logout(request)

    messages.success(
        request,
        "You have been logged out successfully."
    )

    return redirect("login")