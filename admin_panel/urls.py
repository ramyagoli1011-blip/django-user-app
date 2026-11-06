from django.urls import path
from . import views

urlpatterns = [
    path("", views.admin_login, name="admin_login"),
    path("dashboard/", views.dashboard, name="admin_dashboard"),
    path("add-admin/", views.add_admin, name="add_admin"),
    path("logout/", views.admin_logout, name="admin_logout"),
    path("delete-admin/<str:aid>/", views.delete_admin, name="delete_admin"),
    path("admins/", views.admin_list, name="admin_list"),
]