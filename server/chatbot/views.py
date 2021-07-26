from django.shortcuts import render, redirect
from django.views import View
from django.http import HttpResponse
from .AI import main
import importlib
from django.contrib.auth.models import User
import json
# Create your views here.

class Home(View):
    def get(self, request):
        return render(request,'home.html')

class Get(View):
    def get(self, request, *args, **kwargs):
        userText = request.GET.get('msg')
        print(userText)
        return HttpResponse(main.chatbot_response(str(userText)))

class Build(View):
    def get(self, request):
        main.build_model()
        importlib.reload(main)
        return redirect('/')

class Reload(View):
    def get(self, request):
        importlib.reload(main)
        return redirect('/')

class Upload(View):
    def get(self, request):
        if not request.user.is_superuser:
            return redirect('admin/login/?next=/upload')
        return render(request,'upload.html')
    def post(self, request):
        if request.POST.get('tag') is None:
            try:
                f = request.FILES["file"]
                data = json.load(f)
                main.add_data(data)
                main.build_model()
                importlib.reload(main)
                context = {}
                context['result'] = 'Train model complete!'
                return render(request,'result.html',context)
            except Exception as e:
                print(e)
                context = {}
                context['error'] = str(e)
                context['result'] = 'Data format invalid, please check and try again!'
                return render(request,'result.html',context)
        else:
            data = {}
            data['intents'] = []
            intent = {}
            intent['tag'] = request.POST.get('tag')
            intent['patterns'] = []
            intent['patterns'].append(request.POST.get('pattern'))
            intent['responses'] = []
            intent['responses'].append(request.POST.get('response'))
            data['intents'].append(intent)
            try:
                main.add_data(data)
                main.build_model()
                importlib.reload(main)
                context = {}
                context['result'] = 'Train model complete!'
                return render(request,'result.html',context)
            except Exception as e:
                print(e)
                context = {}
                context['error'] = str(e)
                context['result'] = 'Data format invalid, please check and try again!'
                return render(request,'result.html',context)

