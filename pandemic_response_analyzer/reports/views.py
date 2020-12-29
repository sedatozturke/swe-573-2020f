from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from .forms import ReportForm
from .models import Report
from datetime import datetime

def index(request):
    # latest_question_list = Question.objects.order_by('-pub_date')[:5]
    # context = {'latest_question_list': latest_question_list}
    data = Report.objects.all()
    return render(request, 'reports/index.html', {'data': data})

def detail(request, report_id):
    try:
        report = Report.objects.get(pk=report_id)
    except Report.DoesNotExist:
        raise Http404("Q d n e")
    return render(request, 'reports/detail.html', {'report': report})

def new(request):
    msg     = None
    success = False

    if request.method == "POST":
        form = ReportForm(request.POST)
        if form.is_valid():
            form_name = form.cleaned_data['name']
            form_tags = form.cleaned_data['tags']
            form_startdate = datetime.utcnow()
            form_enddate = datetime.utcnow()
            form_status = "Failed"

            report = Report(name=form_name, tags=form_tags, start_date=form_startdate, end_date=form_enddate, status=form_status)
            report.save()

            msg     = ''
            success = True
            
            return redirect("reports:index")
        else:
            msg = 'Form is not valid'    
    else:
        form = ReportForm()
    return render(request, 'reports/new.html', {"form": form, "msg" : msg, "success" : success })

#def results(request, question_id):
#    question = get_object_or_404(Question, pk=question_id)
#    return render(request, 'reports/result.html', { 'question': question })