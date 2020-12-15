from django.shortcuts import render, get_object_or_404
from django.http import Http404

from .models import Question, Choice

def index(request):
    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    context = {'latest_question_list': latest_question_list}
    return render(request, 'reports/index.html', context)

def detail(request, question_id):
    try:
        question = Question.objects.get(pk=question_id)
    except Question.DoesNotExist:
        raise Http404("Q d n e")
    return render(request, 'reports/detail.html', { 'question': question })

def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'reports/result.html', { 'question': question })