from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from .forms import ReportForm
from .models import Report
from datetime import datetime
from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer
from datasources.models import DataSource
from crawler.models import Crawling, Comment, Submission, Subreddit
from collections import Counter
import nltk
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('punkt')
from nltk.corpus import stopwords
from wordcloud import WordCloud, STOPWORDS
import urllib, base64
from io import BytesIO

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
            form_type = form.cleaned_data['report_type']
            form_startdate = datetime.utcnow()
            form_enddate = datetime.utcnow()
            form_status = "Failed"

            textblob_analysis(form_tags)

            # report = Report(name=form_name, tags=form_tags, start_date=form_startdate, end_date=form_enddate, status=form_status, report_type=form_type)
            # report.save()

            msg     = ''
            success = True

            return render(request, 'reports/new.html', {"form": form, "msg" : msg, "success" : success })
            # return redirect("reports:index")
        else:
            msg = 'Form is not valid'    
    else:
        form = ReportForm()
    return render(request, 'reports/new.html', {"form": form, "msg" : msg, "success" : success })

def textblob_analysis(tag):
    datasources = DataSource.objects.filter(tag=tag)
    for datasource in datasources:
        crawls = Crawling.objects.filter(source=datasource, status='Success')
        for crawl in crawls:
            submissions = Submission.objects.filter(crawling=crawl)
            print(len(submissions))
            whole_str = ''
            for submission in submissions:
                whole_str = whole_str + ' ' + submission.title + ' ' + submission.text
            comments = Comment.objects.filter(crawling=crawl)
            for comment in comments:
                whole_str = whole_str + ' ' + comment.body
            
            tb_title = TextBlob(whole_str)
            tb_title_lower = tb_title.lower()
            tb_title_stripped = tb_title_lower.strip()
            words = tb_title_stripped.words
            words = [word for word in words if word.isalpha()]
            stop_words = set(stopwords.words('english'))
            words = [w for w in words if (not w in stop_words and w != 'nt')]
            word_freq = Counter(words)
            wordcloud = WordCloud(width = 800, height = 800, 
                background_color ='white', 
                stopwords = stop_words, 
                min_font_size = 10).generate(whole_str)
            wc_html = wordcloud.to_image()
            buffered = BytesIO()
            wc_html.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue())
            print(img_str)
            common_nouns = word_freq.most_common(50)
            print(common_nouns)
            print(len(comments))

#def results(request, question_id):
#    question = get_object_or_404(Question, pk=question_id)
#    return render(request, 'reports/result.html', { 'question': question })