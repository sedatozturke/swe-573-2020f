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
from textblob import TextBlob, Word
from textblob.sentiments import NaiveBayesAnalyzer
from datasources.models import DataSource
from crawler.models import Crawling, Comment, Submission, Subreddit
from collections import Counter
import tagme
import json
import nltk
import numpy as np
import pandas as pd
import re
import itertools
import unicodedata
import networkx as nx
from scipy.spatial import distance
import matplotlib.pyplot as plt; plt.rcdefaults()
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('punkt')


def index(request):
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
            analysis_success = textblob_analysis(report)
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
            analysis_success = network_analysis(report)
            if analysis_success is True:
                Report.objects.filter(pk=report_id).update(status='Success')
                Report.objects.filter(pk=report_id).update(
                    end_date=datetime.utcnow())
            return render(request, 'reports/detail-loading.html', {"step": step, "step_text": step_text})
        if report.status == 'Success':
            submissions = SubmissionReport.objects.filter(report=report)
            comments = CommentReport.objects.filter(report=report)
            positive_submissions = SubmissionReport.objects.filter(
                report=report, title_sentiment='Positive')
            negative_submissions = SubmissionReport.objects.filter(
                report=report, title_sentiment='Negative')
            neutral_submissions = SubmissionReport.objects.filter(
                report=report, title_sentiment='Neutral')
            positive_comments = CommentReport.objects.filter(
                report=report, body_sentiment='Positive')
            negative_comments = CommentReport.objects.filter(
                report=report, body_sentiment='Negative')
            neutral_comments = CommentReport.objects.filter(
                report=report, body_sentiment='Neutral')
            submission_pie_data = {
                "positive": len(positive_submissions), "negative": len(negative_submissions), "neutral": len(neutral_submissions)
            }
            comment_pie_data = {
                "positive": len(positive_comments), "negative": len(negative_comments), "neutral": len(neutral_comments)
            }
            report_detail = ReportDetail.objects.get(report=report)
            word_count = report_detail.word_count
            word_cloud = report_detail.wordcloud_image_b64
            graph = report_detail.graph_image_b64
            positive_submission_score = report_detail.positive_submission_score
            negative_submission_score = report_detail.negative_submission_score
            positive_comment_score = report_detail.positive_comment_score
            negative_comment_score = report_detail.negative_comment_score
            positive_sb_score_ratio = positive_submission_score/(positive_submission_score+negative_submission_score)
            positive_cm_score_ratio = positive_comment_score/(positive_comment_score+negative_comment_score)

            report_detail_statistics = {
                "num_submissions": len(submissions),
                "num_comments": len(comments),
                "positive_sb_score": positive_submission_score,
                "negative_sb_score": negative_submission_score,
                "positive_cm_score": positive_comment_score,
                "negative_cm_score": negative_comment_score,
                "positive_sb_percent": round((positive_sb_score_ratio*100), 2),
                "negative_sb_percent": round((100-(positive_sb_score_ratio*100)), 2),
                "positive_cm_percent": round((positive_cm_score_ratio*100), 2),
                "negative_cm_percent": round((100-(positive_cm_score_ratio*100)) ,2),
            }
            context = {
                "submission": submission_pie_data,
                "comment": comment_pie_data,
                "word_count": word_count,
                "word_cloud": word_cloud,
                "statistics": report_detail_statistics,
                "report": report,
                "graph": graph
            }
            return render(request, 'reports/detail.html', context=context)
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
            form_tags = form.cleaned_data['tag']
            form_type = form.cleaned_data['report_type']
            form_startdate = datetime.utcnow()
            form_enddate = datetime.utcnow()
            form_status = "Started"

            report = Report(name=form_name, tags=form_tags, start_date=form_startdate,
                            end_date=form_enddate, status=form_status, report_type=form_type)
            report.save()
            msg = ''
            success = True

            return redirect("reports:detail", report.id)
        else:
            msg = 'Form is not valid'
    else:
        form = ReportForm()
    return render(request, 'reports/new.html', {"form": form, "msg": msg, "success": success})


def textblob_analysis(report):
    datasources = DataSource.objects.filter(tag=report.tags, collected=True)
    for datasource in datasources:
        crawls = Crawling.objects.filter(source=datasource, status='Success')
        for crawl in crawls:
            submissions = Submission.objects.filter(crawling=crawl)
            if len(submissions) == 0:
                continue
            whole_str = ''
            positive_submission_score = 0
            negative_submission_score = 0
            positive_comment_score = 0
            negative_comment_score = 0
            for submission in submissions:
                s_report = save_submission_report(
                    submission=submission, report=report)
                score = s_report.submission.score
                if s_report.title_sentiment == 'Positive':
                    positive_submission_score = positive_submission_score + score
                elif s_report.title_sentiment == 'Negative':
                    negative_submission_score = negative_submission_score + score
                whole_str = whole_str + ' ' + submission.title + ' ' + submission.text
            comments = Comment.objects.filter(crawling=crawl)
            for comment in comments:
                c_report = save_comment_report(comment=comment, report=report)
                score = c_report.comment.score
                if c_report.body_sentiment == 'Positive':
                    positive_comment_score = positive_comment_score + score
                elif c_report.body_sentiment == 'Negative':
                    negative_comment_score = negative_comment_score + score
                whole_str = whole_str + ' ' + comment.body

            stop_words = set(stopwords.words('english'))
            stop_words.add('http')
            stop_words.add('https')
            stop_words.add('ca')
            stop_words.add('nt')
            stop_words.add('u')
            stop_words.add('I\'m')
            stop_words.add('com')
            stop_words.add(datasource.source_key)
            common_words, words = word_counter(whole_str, stop_words)
            wc_image = wordcloud_image(words, stop_words)
            wc_image = wc_image[2:-1]
            r_detail = save_report_detail(report=report, cm_words=common_words, wc_image=wc_image, p_s_score=positive_submission_score,
                                          n_s_score=negative_submission_score, p_c_score=positive_comment_score, n_c_score=negative_comment_score)
    return True


def tagme_analysis(tag, report):
    tagme.GCUBE_TOKEN = "8947debe-c147-4d1c-b8af-66eb61352b7b-843339462"
    datasources = DataSource.objects.filter(tag=tag, collected=True)
    for datasource in datasources:
        crawls = Crawling.objects.filter(source=datasource, status='Success')
        for crawl in crawls:
            submissions = Submission.objects.filter(crawling=crawl)
            if len(submissions) == 0:
                continue
            for submission in submissions:
                mentions = tagme.mentions(submission.title)
                men_array = []
                for men in mentions.get_mentions(0.1):
                    mention = men.mention.lower()
                    men_array.append(mention)
                if len(men_array) > 1:
                    print(str(men_array))
    return True

def network_analysis(report):
    stop_words = set(stopwords.words('english'))
    stop_words.add('http')
    stop_words.add('https')
    stop_words.add('ca')
    stop_words.add('nt')
    stop_words.add('u')
    stop_words.add('I\'m')
    stop_words.add('com')
    
    submission_words = []
    datasources = DataSource.objects.filter(tag=report.tags, collected=True)
    for datasource in datasources:
        crawls = Crawling.objects.filter(source=datasource, status='Success')
        for crawl in crawls:
            submissions = Submission.objects.filter(crawling=crawl)
            if len(submissions) == 0:
                continue
            for submission in submissions:
                tb_title = TextBlob(submission.title)
                tb_title_lower = tb_title.lower()
                tb_title_stripped = tb_title_lower.strip()
                words = tb_title_stripped.words
                words = [word for word in words if word.isalpha()]
                words = [w for w in words if (not w in stop_words and len(w) > 1)]
                submission_words.append(words)
        word_cnt = {}
        for words in submission_words:
            for word in words:
                if word not in word_cnt:
                    word_cnt[word] = 1
                else:
                    word_cnt[word] += 1
            
        word_cnt_df = pd.DataFrame({'word': [k for k in word_cnt.keys()], 'cnt': [v for v in word_cnt.values()]})

        vocab = {}
        target_words = word_cnt_df[word_cnt_df['cnt'] > 3]['word'].to_numpy()
        for word in target_words:
            if word not in vocab:
                vocab[word] = len(vocab)

        re_vocab = {}
        for word, i in vocab.items():
            re_vocab[i] = word
        
        tweet_combinations = [list(itertools.combinations(words, 2)) for words in submission_words]
        combination_matrix = np.zeros((len(vocab), len(vocab)))

        for tweet_comb in tweet_combinations:
            for comb in tweet_comb:
                if comb[0] in target_words and comb[1] in target_words:
                    combination_matrix[vocab[comb[0]], vocab[comb[1]]] += 1
                    combination_matrix[vocab[comb[1]], vocab[comb[0]]] += 1
                
        for i in range(len(vocab)):
            combination_matrix[i, i] /= 2

        jaccard_matrix = 1 - distance.cdist(combination_matrix, combination_matrix, 'jaccard')

        nodes = []

        for i in range(len(vocab)):
            for j in range(i+1, len(vocab)):
                jaccard = jaccard_matrix[i, j]
                if jaccard > 0:
                    nodes.append([re_vocab[i], re_vocab[j], word_cnt[re_vocab[i]], word_cnt[re_vocab[j]], jaccard])
        print(len(nodes))

        G = nx.Graph()
        G.nodes(data=True)

        for pair in nodes:
            node_x, node_y, node_x_cnt, node_y_cnt, jaccard = pair[0], pair[1], pair[2], pair[3], pair[4]
            if not G.has_node(node_x):
                G.add_node(node_x, count=node_x_cnt)
            if not G.has_node(node_y):
                G.add_node(node_y, count=node_y_cnt)
            if not G.has_edge(node_x, node_y):
                G.add_edge(node_x, node_y, weight=jaccard)
                
        plt.figure(figsize=(12,12))
        pos = nx.spring_layout(G, k=0.5)

        node_size = [d['count']*100 for (n,d) in G.nodes(data=True)]
        nx.draw_networkx_nodes(G, pos, node_color='cyan', alpha=1.0, node_size=node_size)
        nx.draw_networkx_labels(G, pos, font_size=10)

        edge_width = [d['weight']*10 for (u,v,d) in G.edges(data=True)]
        nx.draw_networkx_edges(G, pos, alpha=0.2, edge_color='black', width=edge_width)

        plt.axis('off')
        buffered = BytesIO()
        plt.savefig(buffered, format="JPEG")
        img_str = str(base64.b64encode(buffered.getvalue()))
        graph_image = img_str[2:-1]
        ReportDetail.objects.filter(report=report).update(graph_image_b64=graph_image)

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
        submission_report = SubmissionReport.objects.get(
            submission=submission, report=report)
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
        comment_report = CommentReport.objects.get(
            comment=comment, report=report)
        return comment_report
    except CommentReport.DoesNotExist:
        tb_com = TextBlob(comment.body)
        com_sentiment = tb_com.sentiment
        com_sentiment_res = 'Neutral'
        if com_sentiment.polarity >= 0.01:
            com_sentiment_res = 'Positive'
        elif com_sentiment.polarity <= -0.01:
            com_sentiment_res = 'Negative'
        comment_report = CommentReport(report=report, comment=comment, body_polarity=com_sentiment.polarity,
                                       body_subjectivity=com_sentiment.subjectivity, body_sentiment=com_sentiment_res)
        comment_report.save()
        return comment_report


def save_report_detail(report, cm_words, wc_image, p_s_score, n_s_score, p_c_score, n_c_score):
    try:
        report_detail = ReportDetail.objects.get(report=report)
        return report_detail
    except ReportDetail.DoesNotExist:
        report_detail = ReportDetail(report=report, wordcloud_image_b64=wc_image, word_count=json.dumps(
            cm_words), positive_submission_score=p_s_score, negative_submission_score=n_s_score, positive_comment_score=p_c_score, negative_comment_score=n_c_score)
        report_detail.save()
        return report_detail
