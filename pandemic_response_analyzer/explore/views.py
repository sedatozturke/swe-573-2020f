from django.shortcuts import render, get_object_or_404
from django.http import Http404
import praw
import datetime as dt
from .forms import SearchForm
from .models import Subreddit
from datetime import datetime
from textblob import TextBlob
import tagme

def index(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            keyword = form.cleaned_data['keyword']
            reddit = praw.Reddit(client_id='pcZsViT7EcP8WQ',
                                 client_secret='iJtPC9Tmdyk96hd3cUvmuyrmAFMJXA',
                                 user_agent='swe-573-student-project')
            tagme.GCUBE_TOKEN = "8947debe-c147-4d1c-b8af-66eb61352b7b-843339462"
            subreddit = reddit.subreddit(keyword)
            new_sr = subreddit.new(limit=100)
            for submission in new_sr:
                analysis = TextBlob(submission.title)
                annotations = tagme.annotate(submission.title)
                for ann in annotations.get_annotations(0.1):
                    print(ann)
                mentions = tagme.mentions(submission.title)
                for mention in mentions.mentions:
                    print(mention)
                sub = Subreddit(title=submission.title, reddit_id=submission.id, created_utc=datetime.utcfromtimestamp(submission.created_utc),
                                score=submission.score, name=submission.name, upvote_ratio=submission.upvote_ratio, polarity=analysis.sentiment.polarity, subjectivity=analysis.sentiment.subjectivity)

                sub.save()
                # for comment in submission.comments:
                #    print(comment.body)
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            data = Subreddit.objects.all()
            print("data")
            print(data)
            return render(request, 'explore/index.html', { 'data': data })
    
    data = Subreddit.objects.all()
    print("data")
    print(data)
    return render(request, 'explore/index.html')