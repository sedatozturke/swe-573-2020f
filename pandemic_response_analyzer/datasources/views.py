from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from .forms import DataSourceForm
from datetime import datetime
from .models import DataSource
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    data = DataSource.objects.all()
    return render(request, 'datasources/index.html', {'data': data})

@login_required
def new(request):
    msg     = None
    success = False

    if request.method == "POST":
        form = DataSourceForm(request.POST)
        if form.is_valid():
            form_platform = form.cleaned_data['platform']
            form_source_type = form.cleaned_data['source_type']
            form_source_key = form.cleaned_data['source_key']
            form_tag = form.cleaned_data['tag']
            form_weight = form.cleaned_data['limit']
            form_date = datetime.utcnow()

            datasource = DataSource(platform = form_platform, tag = form_tag, source_type = form_source_type, source_key = form_source_key, limit = form_weight, pub_date = form_date)
            datasource.save()

            msg     = 'User created - please <a href="/login">login</a>.'
            success = True
            
            return redirect("datasources:index")
        else:
            msg = 'Form is not valid'    
    else:
        form = DataSourceForm()
    return render(request, 'datasources/new.html', {"form": form, "msg" : msg, "success" : success })