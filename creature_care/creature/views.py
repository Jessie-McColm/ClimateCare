from django.shortcuts import render
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.views import generic
from django.utils import timezone

# Create your views here.


def kitty(request):
    return HttpResponse("Hello, world. You're at the kitty.")

def articles(request):
    return HttpResponse("article page")
