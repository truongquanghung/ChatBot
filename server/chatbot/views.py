from django.shortcuts import render, redirect
from django.views import View
from django.http import HttpResponse
from .AI import main
import importlib

# Create your views here.

class Home(View):
    def get(self, request):
        return render(request,'home.html')

class Get(View):
    def get(self, request, *args, **kwargs):
        userText = request.GET.get('msg')
        print(userText)
        return HttpResponse(main.chatbot_response(str(userText)))

class Reload(View):
    def get(self, request):
        importlib.reload(main)
        return redirect('/')