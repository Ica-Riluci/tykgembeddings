from django.shortcuts import render
from django.http import HttpResponse

def mew(request):
    return HttpResponse(render(request, 'search_experienced_worker.html'))

def simple_query(request):
    return HttpResponse(render(request, 'simple_query.html'))

def special_query1(request):
    return HttpResponse(render(request, 'special_query1.html'))


# Create your views here.