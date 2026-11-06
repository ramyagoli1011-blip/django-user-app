from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password, make_password
from django.utils import timezone

from admin_panel.db import get_admins
from register.db import get_users

from bson import ObjectId
from pymongo.errors import DuplicateKeyError


# Check logged-in admin
def get_admin(request):
    aid = request.session.get("admin_id")

    if not aid:
        return None

    try:
        admin = get_admins().find_one({
            "_id": ObjectId(aid),
            "active": True
        })

        return admin

    except Exception:
        return None


# Admin Login
def admin_login(request):
    current = get_admin(request)

    if current:
        return redirect("/admin-panel/dashboard/")

    request.session.flush()
    error = ""

    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")

        admin = get_admins().find_one({"email": email})

        if admin and admin.get("active") is True:
            if check_password(password, admin.get("password", "")):
                request.session.flush()
                request.session["admin_id"] = str(admin["_id"])

                return redirect("/admin-panel/dashboard/")

        error = "Invalid email or password."

    return render(request, "admin_login.html", {"error": error})


# Admin Dashboard
def dashboard(request):
    admin = get_admin(request)

    if not admin:
        return redirect("/admin-panel/")

    users = list(get_users().find({}, {"password": 0}))

    for user in users:
        user["id"] = str(user["_id"])

    return render(
        request,
        "admin_dashboard.html",
        {
            "users": users,
            "total": len(users),
            "admin_email": admin["email"],
            "admin_role": admin["role"],
        }
    )


# Add Admin
def add_admin(request):
    admin = get_admin(request)

    if not admin:
        return redirect("/admin-panel/")

    if admin.get("role") != "super_admin":
        return redirect("/admin-panel/dashboard/")

    error = ""
    success = ""

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")

        if not name or not email or not password:
            error = "All fields are required."

        elif len(password) < 8:
            error = "Password must contain at least 8 characters."

        else:
            admins = get_admins()
            admins.create_index("email", unique=True)

            try:
                admins.insert_one({
                    "name": name,
                    "email": email,
                    "password": make_password(password),
                    "role": "admin",
                    "active": True,
                    "created_at": timezone.now()
                })

                success = "Admin created successfully!"

            except DuplicateKeyError:
                error = "This email is already registered."

    return render(
        request,
        "add_admin.html",
        {
            "error": error,
            "success": success
        }
    )


# Admin List
def admin_list(request):
    admin = get_admin(request)

    if not admin:
        return redirect("/admin-panel/")

    if admin.get("role") != "super_admin":
        return redirect("/admin-panel/dashboard/")

    admins = list(
        get_admins().find({}, {"password": 0})
    )

    for item in admins:
        item["id"] = str(item["_id"])

    return render(
        request,
        "admin_list.html",
        {"admins": admins}
    )


# Delete Admin
def delete_admin(request, aid):
    admin = get_admin(request)

    if not admin:
        return redirect("/admin-panel/")

    if admin.get("role") != "super_admin":
        return redirect("/admin-panel/dashboard/")

    if request.method == "POST":
        try:
            admins = get_admins()
            target = admins.find_one({"_id": ObjectId(aid)})

            if (
                target
                and target.get("role") != "super_admin"
                and str(target["_id"]) != str(admin["_id"])
            ):
                admins.delete_one({"_id": target["_id"]})

        except Exception:
            pass

    return redirect("/admin-panel/admins/")


# Admin Logout
def admin_logout(request):
    request.session.flush()
    return redirect("/admin-panel/")