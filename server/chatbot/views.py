from django.shortcuts import render, redirect
from django.views import View
from django.http import HttpResponse
from .AI import main
import importlib
from django.contrib.auth.models import User
import json
from googletrans import Translator
# Create your views here.

class Home(View):
    def get(self, request):
        return render(request,'home.html')

class Get(View):
    def get(self, request):
        userText = request.GET.get('msg')
        translator = Translator(service_urls=['translate.googleapis.com'])
        res = translator.translate(userText, dest='en')
        print(res.text)
        response = translator.translate(main.chatbot_response(res.text), dest=res.src)
        return HttpResponse(response.text)

class Tag(View):
    def get(self, request):
        data = {
            'tag': main.list_tag()
        }
        return render(request, 'tag.html', data)

class Intent(View):
    def get(self, request, tag):
        data = {
            'tag': tag,
            'intent': main.list_intent(tag)
        }
        return render(request, 'intent.html', data)

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

