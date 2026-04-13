

# Create your views here.
from django.shortcuts import render
from .models import Question

def index(request):
    questions = Question.objects.all()
    return render(request, 'polls/index.html', {'questions': questions})