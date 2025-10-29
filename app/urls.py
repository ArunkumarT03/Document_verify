from django.urls import path
from app.views import *

urlpatterns=[
    path('signin/',SigninView.as_view(),name='signin'),
    path('doc/',VerifyDocumentsView.as_view(),name='doc')
]