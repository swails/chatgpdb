from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("chat/<str:pdb_id>/", views.pdb, name="pdb"),
]