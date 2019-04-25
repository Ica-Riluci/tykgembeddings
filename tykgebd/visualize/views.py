from django.shortcuts import render
from django.http import HttpResponse

def simple_query(request):
    return HttpResponse(render(request, 'simple_query.html'))

def special_query1(request):
    return HttpResponse(render(request, 'special_query1.html'))

def special_query2(request):
    return HttpResponse(render(request, 'special_query2.html'))

def special_query3(request):
    return HttpResponse(render(request, 'special_query3.html'))
# Create your views here.
