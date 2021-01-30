from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from datetime import datetime
from .forms import CrawlerForm
from .models import Crawling
from datasources.models import DataSource
import praw


def index(request):
    # latest_question_list = Question.objects.order_by('-pub_date')[:5]
    # context = {'latest_question_list': latest_question_list}
    data = Crawling.objects.all()
    return render(request, 'crawler/index.html', {'data': data})


def detail(request, report_id):
    # try:
    #    report = Report.objects.get(pk=report_id)
    # except Report.DoesNotExist:
    #    raise Http404("Q d n e")
    return render(request, 'crawler/detail.html')


def crawl(request):
    if request.method == 'POST':
        form = CrawlerForm(request.POST)
        if form.is_valid():
            keyword = form.cleaned_data['keyword']
            reddit = praw.Reddit(client_id='pcZsViT7EcP8WQ',
                                 client_secret='iJtPC9Tmdyk96hd3cUvmuyrmAFMJXA',
                                 user_agent='swe-573-student-project')
            # tagme.GCUBE_TOKEN = "8947debe-c147-4d1c-b8af-66eb61352b7b-843339462"
            subreddit = reddit.subreddit(keyword)
            new_sr = subreddit.new(limit=100)
            for submission in new_sr:
                print(submission)
                #analysis = TextBlob(submission.title)
                #annotations = tagme.annotate(submission.title)
                #for ann in annotations.get_annotations(0.1):
                #    print(ann)
                #mentions = tagme.mentions(submission.title)
                #for mention in mentions.mentions:
                #    print(mention)
                #sub = Subreddit(title=submission.title, reddit_id=submission.id, created_utc=datetime.utcfromtimestamp(submission.created_utc),
                #                score=submission.score, name=submission.name, upvote_ratio=submission.upvote_ratio, polarity=analysis.sentiment.polarity, subjectivity=analysis.sentiment.subjectivity)

                #sub.save()
                # for comment in submission.comments:
                #    print(comment.body)
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            #data = Subreddit.objects.all()
            #print("data")
            #print(data)
            return render(request, 'explore/index.html')
    
    #data = Subreddit.objects.all()
    #print("data")
    #print(data)
    return render(request, 'explore/index.html')

def new(request):
    msg = None
    success = False

    if request.method == "POST":
        form = CrawlerForm(request.POST)
        if form.is_valid():
            datasource = DataSource.objects.get(pk=form.cleaned_data['datasource_id'])
            form_startdate = datetime.utcnow()

            # report = Crawling(source=datasource, start_date=form_startdate)
            # report.save()

            reddit = praw.Reddit(client_id='pcZsViT7EcP8WQ',
                                 client_secret='iJtPC9Tmdyk96hd3cUvmuyrmAFMJXA',
                                 user_agent='swe-573-student-project')
            subreddit = reddit.subreddit(datasource.source_key)
            new_sr = subreddit.new(limit=100)
            for submission in new_sr:
                print(submission.name + ": " + str(submission.num_comments) + " - " + submission.title + " - " + submission.selftext)
                for comment in submission.comments:
                    print(comment.id + ": " + comment.body + " - " + comment.link_id)

            msg = ''
            success = True

            return render(request, 'crawler/new.html', {"form": form, "msg" : msg, "success" : success })
        else:
            msg = 'Form is not valid'
    else:
        form = CrawlerForm()
    return render(request, 'crawler/new.html', {"form": form, "msg" : msg, "success" : success })

# def results(request, question_id):
#    question = get_object_or_404(Question, pk=question_id)
#    return render(request, 'reports/result.html', { 'question': question })
