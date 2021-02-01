import base64
import urllib
from io import BytesIO
from wordcloud import WordCloud, STOPWORDS
from nltk.corpus import stopwords
from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from .forms import ReportForm
from .models import Report, ReportDetail, SubmissionReport, CommentReport
from datetime import datetime
from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer
from datasources.models import DataSource
from crawler.models import Crawling, Comment, Submission, Subreddit
from collections import Counter
import json
import nltk
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('punkt')


def index(request):
    # latest_question_list = Question.objects.order_by('-pub_date')[:5]
    # context = {'latest_question_list': latest_question_list}
    data = Report.objects.all()
    return render(request, 'reports/index.html', {'data': data})


def detail(request, report_id):
    try:
        report = Report.objects.get(pk=report_id)
        if report.status == 'Started':
            step = "1"
            step_text = "Analysis with Textblob"
            Report.objects.filter(pk=report_id).update(status='Textblob')
            return render(request, 'reports/detail-loading.html', {"step": step, "step_text": step_text})
        if report.status == 'Textblob':
            step = "2"
            step_text = "Analysis with TagMe"
            analysis_success = textblob_analysis(report.tags, report)
            if analysis_success is True:
                Report.objects.filter(pk=report_id).update(status='Tagme')  
            return render(request, 'reports/detail-loading.html', {"step": step, "step_text": step_text})
        if report.status == 'Tagme':
            step = "3"
            step_text = "Entity Network Analysis"
            analysis_success = True
            if analysis_success is True:
                Report.objects.filter(pk=report_id).update(status='Network')
            return render(request, 'reports/detail-loading.html', {"step": step, "step_text": step_text})
        if report.status == 'Network':
            step = "4"
            step_text = "Finalizing"
            analysis_success = True
            if analysis_success is True:
                Report.objects.filter(pk=report_id).update(status='Success')
                Report.objects.filter(pk=report_id).update(end_date=datetime.utcnow())
            return render(request, 'reports/detail-loading.html', {"step": step, "step_text": step_text})
        if report.status == 'Success':
            positive_submissions = SubmissionReport.objects.filter(report=report, title_sentiment='Positive').count
            negative_submissions = SubmissionReport.objects.filter(report=report, title_sentiment='Negative').count
            neutral_submissions = SubmissionReport.objects.filter(report=report, title_sentiment='Neutral').count
            positive_comments = CommentReport.objects.filter(report=report, body_sentiment='Positive').count
            negative_comments = CommentReport.objects.filter(report=report, body_sentiment='Negative').count
            neutral_comments = CommentReport.objects.filter(report=report, body_sentiment='Neutral').count
            submission_pie_data = {
                "positive": positive_submissions, "negative": negative_submissions, "neutral": neutral_submissions
            }
            comment_pie_data = {
                "positive": positive_comments, "negative": negative_comments, "neutral": neutral_comments
            }
            report_detail = ReportDetail.objects.get(report=report)
            word_count = report_detail.word_count
            word_cloud = report_detail.wordcloud_image_b64
            return render(request, 'reports/detail.html', { "submission": submission_pie_data, "comment": comment_pie_data, "word_count": word_count, "word_cloud": word_cloud })
    except Report.DoesNotExist:
        raise Http404("Q d n e")
    return render(request, 'reports/detail-loading.html')


def new(request):
    msg = None
    success = False

    if request.method == "POST":
        form = ReportForm(request.POST)
        if form.is_valid():
            form_name = form.cleaned_data['name']
            form_tags = form.cleaned_data['tags']
            form_type = form.cleaned_data['report_type']
            form_startdate = datetime.utcnow()
            form_enddate = datetime.utcnow()
            form_status = "Started"

            # textblob_analysis(form_tags)

            report = Report(name=form_name, tags=form_tags, start_date=form_startdate,
                            end_date=form_enddate, status=form_status, report_type=form_type)
            report.save()
            msg = ''
            success = True

            # return render(request, 'reports/new.html', {"form": form, "msg" : msg, "success" : success })
            return redirect("reports:detail", report.id)
        else:
            msg = 'Form is not valid'
    else:
        form = ReportForm()
    return render(request, 'reports/new.html', {"form": form, "msg": msg, "success": success})


def textblob_analysis(tag, report):
    datasources = DataSource.objects.filter(tag=tag)
    for datasource in datasources:
        crawls = Crawling.objects.filter(source=datasource, status='Success')
        for crawl in crawls:
            submissions = Submission.objects.filter(crawling=crawl)
            whole_str = ''
            for submission in submissions:
                s_report = save_submission_report(submission=submission, report=report)
                whole_str = whole_str + ' ' + submission.title + ' ' + submission.text
            comments = Comment.objects.filter(crawling=crawl)
            for comment in comments:
                c_report = save_comment_report(comment=comment, report=report)
                whole_str = whole_str + ' ' + comment.body

            stop_words = set(stopwords.words('english'))
            stop_words.add('http')
            stop_words.add('https')
            stop_words.add('ca')
            stop_words.add('nt')
            stop_words.add('u')
            stop_words.add('I\'m')
            stop_words.add('com')
            common_words, words = word_counter(whole_str, stop_words)
            wc_image = wordcloud_image(words, stop_words)
            wc_image = wc_image[2:-1]
            r_detail = save_report_detail(report=report, cm_words=common_words, wc_image=wc_image)
    return True


def word_counter(text, stop_words):
    tb_title = TextBlob(text)
    tb_title_lower = tb_title.lower()
    tb_title_stripped = tb_title_lower.strip()
    words = tb_title_stripped.words
    words = [word for word in words if word.isalpha()]
    words = [w for w in words if (not w in stop_words and len(w) > 1)]
    word_freq = Counter(words)
    most_common_words = word_freq.most_common(50)
    return most_common_words, words


def naive_bayes_analysis(tag):
    datasources = DataSource.objects.filter(tag=tag)
    for datasource in datasources:
        crawls = Crawling.objects.filter(source=datasource, status='Success')
        for crawl in crawls:
            submissions = Submission.objects.filter(crawling=crawl)
            for submission in submissions:
                blob_object = TextBlob(
                    submission.title, analyzer=NaiveBayesAnalyzer())
            comments = Comment.objects.filter(crawling=crawl)
            for comment in comments:
                blob_object = TextBlob(
                    comment.body, analyzer=NaiveBayesAnalyzer())


def wordcloud_image(text, stop_words):
    wordcloud = WordCloud(width=500, height=200,
                          background_color='white',
                          stopwords=stop_words,
                          min_font_size=10).generate(" ".join(text))
    wc_image = wordcloud.to_image()
    buffered = BytesIO()
    wc_image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue())
    return str(img_str)

def save_submission_report(submission, report):
    try:
        submission_report = SubmissionReport.objects.get(submission=submission, report=report)
        return submission_report
    except SubmissionReport.DoesNotExist:
        tb_sub = TextBlob(submission.title)
        tb_sub_text = TextBlob(submission.text)
        title_sentiment = tb_sub.sentiment
        text_sentiment = tb_sub_text.sentiment
        title_sentiment_res = 'Neutral'
        text_sentiment_res = 'Neutral'
        if title_sentiment.polarity >= 0.01:
            title_sentiment_res = 'Positive'
        elif title_sentiment.polarity <= -0.01:
            title_sentiment_res = 'Negative'
        if text_sentiment.polarity >= 0.01:
            text_sentiment_res = 'Positive'
        elif text_sentiment.polarity <= -0.01:
            text_sentiment_res = 'Negative'
        submission_report = SubmissionReport(submission=submission, report=report, title_polarity=title_sentiment.polarity, title_subjectivity=title_sentiment.subjectivity,
                                                     title_sentiment=title_sentiment_res, text_polarity=text_sentiment.polarity, text_subjectivity=text_sentiment.subjectivity, text_sentiment=text_sentiment_res)
        submission_report.save()
        return submission_report

def save_comment_report(comment, report):
    try:
        comment_report = CommentReport.objects.get(comment=comment, report=report)
        return comment_report
    except CommentReport.DoesNotExist:
        tb_com = TextBlob(comment.body)
        com_sentiment = tb_com.sentiment
        com_sentiment_res = 'Neutral'
        if com_sentiment.polarity >= 0.01:
            com_sentiment_res = 'Positive'
        elif com_sentiment.polarity <= -0.01:
            com_sentiment_res = 'Negative'
        comment_report = CommentReport(report=report, comment=comment, body_polarity=com_sentiment.polarity, body_subjectivity=com_sentiment.subjectivity, body_sentiment=com_sentiment_res)
        comment_report.save()
        return comment_report

def save_report_detail(report, cm_words, wc_image):
    try:
        report_detail = ReportDetail.objects.get(report=report)
        return report_detail
    except ReportDetail.DoesNotExist:
        report_detail = ReportDetail(report=report, wordcloud_image_b64=wc_image, word_count=json.dumps(cm_words))
        report_detail.save()
        return report_detail

