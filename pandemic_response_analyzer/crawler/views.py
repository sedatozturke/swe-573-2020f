from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from datetime import datetime
from .forms import CrawlerForm
from .models import Crawling, Comment, Submission, Subreddit
from datasources.models import DataSource
import praw
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    # latest_question_list = Question.objects.order_by('-pub_date')[:5]
    # context = {'latest_question_list': latest_question_list}
    data = Crawling.objects.all()
    return render(request, 'crawler/index.html', {'data': data})

@login_required
def detail(request, crawl_id):
    try:
        crawler = Crawling.objects.get(pk=crawl_id)
        submissions = Submission.objects.filter(crawling=crawler)
        data = []
        for submission in submissions:
            comments = Comment.objects.filter(submission=submission)
            item = { 'submission': submission, 'num_col_comments': len(comments), 'comments': comments}
            data.append(item)
    except Crawling.DoesNotExist:
        raise Http404("Q d n e")
    return render(request, 'crawler/detail.html', {'crawler': crawler, 'data': data})


def save_subreddit(subreddit, crawler):
    try:
        sr = Subreddit.objects.get(subreddit_id=subreddit.id)
        return sr
    except Subreddit.DoesNotExist:
        sr = Subreddit(created_utc=datetime.utcnow(), subreddit_created_utc=datetime.utcfromtimestamp(subreddit.created_utc), subreddit_id=subreddit.id, subreddit_full_id=subreddit.name, description=subreddit.description,
                           public_description=subreddit.public_description, display_name=subreddit.display_name, subscriber_count=subreddit.subscribers, crawling=crawler)
        sr.save()
        return sr

def save_submission(submission, subreddit, crawler):
    try:
        sub = Submission.objects.get(submission_id=submission.id)
        return sub
    except Submission.DoesNotExist:
        sub = Submission(created_utc=datetime.utcnow(), submission_created_utc=datetime.utcfromtimestamp(submission.created_utc), submission_id=submission.id, submission_full_id=submission.name, num_all_comments=submission.num_comments,
                                 score=submission.score, upvote_ratio=submission.upvote_ratio, text=submission.selftext, title=submission.title, subreddit=subreddit, crawling=crawler)
        sub.save()
        return sub

def save_comment(comment, subreddit, submission, crawler):
    try:
        com = Comment.objects.get(comment_id=comment.id)
        return com
    except Comment.DoesNotExist:
        com = Comment(created_utc=datetime.utcnow(), comment_created_utc=datetime.utcfromtimestamp(comment.created_utc), score=comment.score, subreddit=subreddit,
                                  comment_id=comment.id, parent_id=comment.parent_id, comment_subreddit_id=comment.subreddit_id, body=comment.body, submission=submission, crawling=crawler)
        com.save()
        return com

@login_required
def new(request):
    msg = None
    success = False

    if request.method == "POST":
        form = CrawlerForm(request.POST)
        if form.is_valid():
            datasource = DataSource.objects.get(
                pk=form.cleaned_data['datasource_id'])
            date_now = datetime.utcnow()

            crawler = Crawling(source=datasource, start_date=date_now, status='Failed')
            crawler.save()

            reddit = praw.Reddit(client_id='pcZsViT7EcP8WQ',
                                 client_secret='iJtPC9Tmdyk96hd3cUvmuyrmAFMJXA',
                                 user_agent='swe-573-student-project')
            subreddit = reddit.subreddit(datasource.source_key)
            sr = save_subreddit(subreddit, crawler)

            submissions = subreddit.new(limit=datasource.limit)   
            for submission in submissions:
                sub = save_submission(submission, sr, crawler)
                for comment in submission.comments:
                    save_comment(comment, sr, sub, crawler)

            Crawling.objects.filter(id=crawler.id).update(status='Success')
            DataSource.objects.filter(id=form.cleaned_data['datasource_id']).update(collected=True)

            msg = ''
            success = True

            return redirect('crawler:detail', crawler.id)
        else:
            msg = 'Form is not valid'
    else:
        form = CrawlerForm()
    return render(request, 'crawler/new.html', {"form": form, "msg": msg, "success": success})

