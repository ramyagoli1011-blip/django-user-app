
import re
from datetime import date

from bson import ObjectId
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.http import require_http_methods

from .db import get_users


def home(request):
    return render(request, "home.html")


def show_error(request, msg):
    return render(request, "register.html", {"error": msg})


@require_http_methods(["GET", "POST"])
def register(request):
    if request.method == "GET":
        return render(request, "register.html")

    data = request.POST

    name = data.get("name", "").strip()
    dob = data.get("dob", "")
    gender = data.get("gender", "")
    email = data.get("email", "").strip().lower()
    code = data.get("code", "")
    mobile = data.get("mobile", "").strip()
    address = data.get("address", "").strip()
    country = data.get("country", "")
    state = data.get("state", "")
    district = data.get("district", "")
    city = data.get("city", "").strip()
    pin = data.get("pin", "").strip()
    username = data.get("username", "").strip()
    password = data.get("password", "")
    confirm = data.get("confirm", "")

    # Terms validation
    if not data.get("terms"):
        return show_error(
            request,
            "Please accept the Terms and Conditions."
        )

    # Required fields
    if not name or not email or not dob or not username:
        return show_error(
            request,
            "Please fill all required fields."
        )

    # Username validation
    if not re.fullmatch(r"[A-Za-z0-9_]{4,30}", username):
        return show_error(
            request,
            "Username must contain 4-30 letters, numbers or underscores."
        )

    # Email validation
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return show_error(
            request,
            "Enter a valid email address."
        )

    # Mobile validation
    if not re.fullmatch(r"[0-9]{10}", mobile):
        return show_error(
            request,
            "Mobile number must contain 10 digits."
        )

    # PIN validation
    if not re.fullmatch(r"[0-9]{6}", pin):
        return show_error(
            request,
            "PIN code must contain 6 digits."
        )

    # Password validation
    if not re.fullmatch(
        r"(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}",
        password
    ):
        return show_error(
            request,
            "Password must be at least 8 characters and include uppercase, lowercase, number and special character."
        )

    # Confirm password
    if password != confirm:
        return show_error(
            request,
            "Passwords do not match."
        )

    # Date of birth validation
    try:
        birth = date.fromisoformat(dob)

        if birth >= date.today():
            return show_error(
                request,
                "Enter a valid date of birth."
            )

    except ValueError:
        return show_error(
            request,
            "Enter a valid date of birth."
        )

    # Photo validation
    photo = request.FILES.get("photo")
    photo_data = None

    if photo:
        if photo.size > 2 * 1024 * 1024:
            return show_error(
                request,
                "Photo must be 2 MB or smaller."
            )

        if photo.content_type not in (
            "image/jpeg",
            "image/png",
            "image/webp"
        ):
            return show_error(
                request,
                "Upload a JPG, PNG or WEBP photo."
            )

        photo_data = {
            "name": photo.name,
            "type": photo.content_type,
            "data": photo.read()
        }

    # Save user in MongoDB
    try:
        users = get_users()

        if users.find_one({"email": email}):
            return show_error(
                request,
                "This email is already registered."
            )

        if users.find_one({"username": username}):
            return show_error(
                request,
                "This username is already taken."
            )

        user = {
            "name": name,
            "dob": dob,
            "gender": gender,
            "email": email,
            "code": code,
            "mobile": mobile,
            "address": address,
            "country": country,
            "state": state,
            "district": district,
            "city": city,
            "pin": pin,
            "username": username,
            "password": make_password(password),
            "photo": photo_data,
        }

        users.insert_one(user)

    except Exception as e:
        print("REGISTRATION ERROR:", repr(e))

        return show_error(
            request,
            "Registration service is unavailable. Please try again later."
        )

    return redirect("/success/")


def success(request):
    return render(request, "success.html")


@require_http_methods(["GET", "POST"])
def login(request):
    if request.method == "GET":
        return render(request, "login.html")

    value = request.POST.get("username", "").strip()
    password = request.POST.get("password", "")

    if not value or not password:
        return render(
            request,
            "login.html",
            {"error": "Enter your username/email and password."}
        )

    try:
        users = get_users()

        user = users.find_one({
            "$or": [
                {"username": value},
                {"email": value.lower()}
            ]
        })

        if not user or not check_password(
            password,
            user.get("password", "")
        ):
            return render(
                request,
                "login.html",
                {"error": "Invalid username/email or password."}
            )

        request.session.cycle_key()
        request.session["user_id"] = str(user["_id"])

    except Exception as e:
        print("LOGIN ERROR:", repr(e))

        return render(
            request,
            "login.html",
            {"error": "Login service is unavailable. Please try again."}
        )

    return redirect("/welcome/")


def welcome(request):
    uid = request.session.get("user_id")

    if not uid:
        return redirect("/login/")

    try:
        users = get_users()

        user = users.find_one(
            {"_id": ObjectId(uid)},
            {"password": 0}
        )

        if not user:
            request.session.flush()
            return redirect("/login/")

        return render(
            request,
            "welcome.html",
            {"user": user}
        )

    except Exception as e:
        print("WELCOME ERROR:", repr(e))

        return render(
            request,
            "welcome.html",
            {"error": "Unable to load user details."}
        )


def logout(request):
    request.session.flush()
    return redirect("/login/")
