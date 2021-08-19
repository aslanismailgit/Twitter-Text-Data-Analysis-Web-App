
from twan import app
from twan import mail
from twan.functions import TWAN
from twan.functions import *
from twan.correlation_fuctions import *
from twan import model_ser_encoder
from twan.sentiment_functions import *
from twan.word_cooc_functions import *
from twan.forms import SearchInputForm, TargetWordsForm, SentimentForm, EmailDownloadForm, WordCoocForm
from twan.models import searchitems
from twan import db
# from twan import mongo
# from bson.objectid import ObjectId

import pandas as pd
from datetime import datetime
from re import search

from flask import render_template, session, redirect, url_for 
from flask import send_from_directory, request
from flask import flash

sendemail_flag = 1

#%%
@app.route('/download/<zip_dir_name>', methods=['GET', 'POST'])
def email_link(zip_dir_name):
    filename = zip_dir_name + ".zip"
    path = os.path.join(app.root_path, 
                        session['cur_data_dir'].replace("twan/", ""))
    return send_from_directory(directory=path, 
                                path=filename, 
                                as_attachment=True)


@app.route('/download', methods=['GET', 'POST'])
def download_page():
    form = EmailDownloadForm()
    if request.method=="POST":
        if form.validate_on_submit:
            session['email'] = form.email.data
            current_dir = session["cur_data_dir"]
            zip_dir_name = copy2zip(current_dir)
            download_link = f'http://127.0.0.1:5000/download/{zip_dir_name}'
            session['zip_dir_name'] = zip_dir_name
            recipients = session['email']
            if sendemail_flag == 1:
                send_email(recipients, download_link)
            # print('-----download route-------session["search_id"]------------------', session["search_id"])
            item = searchitems.query.filter_by(id=session["search_id"]).first()
            item.email_address = session['email']
            db.session.commit()  

            return render_template('download_page.html', 
                                form=form,
                                download_link=download_link)

    return render_template('download_page.html', 
                                form=form)

# to run loading page to route is created 
@app.route('/word_cooc', methods=['GET', 'POST'])
def word_cooc_page():
    form = WordCoocForm()
    if request.method=="POST":
        session['top_n_words'] = form.top_n_words.data
        print("session['top_n_words']", session['top_n_words'])
        return redirect(url_for('target_word_cooc'))
    
    return render_template('word_cooc_page.html', 
                                form=form)

@app.route('/word_cooc_compute', methods=['GET', 'POST'])
def word_cooc_compute():
    form = WordCoocForm()
    if request.method=="POST":
        if form.validate_on_submit:
            session['top_n_words'] = form.top_n_words.data
            print("session['top_n_words']", session['top_n_words'])
            return redirect(url_for('target_word_cooc'))

    x = "_" + str(session['top_n_words']) 
    fname = session["cur_data_dir"] + "/" + "fig_word_cooc" + x  + ".txt"
    if os.path.isfile(fname):
        with open(fname) as f:
            fig = f.read()
        return render_template('word_cooc_page.html',
                            fig = fig,
                            form=form,
                             )
    
    df_path = session["cur_data_dir"] + "/" 
    top_n_words = session['top_n_words']
    fig, df_tweets = word_cooc_main(df_path, top_n_words)
    current_dir = session["cur_data_dir"]
    df_tweets.to_csv(current_dir + "/" + "tweets_collected.csv", index=False)    
    
    with open(fname, "w") as f:
        f.write(fig)
    
    return render_template('word_cooc_page.html',
                            fig = fig,
                            form=form,
                             )


# to run loading page to route is created 
@app.route('/sentiment', methods=['GET', 'POST'])
def sentiment_page():
    form = SentimentForm()
    if request.method=="POST":
        return redirect(url_for('target_sentiment'))
    
    return render_template('sentiment_page.html', 
                                form=form)

@app.route('/sentiment_compute', methods=['GET', 'POST'])
def sentiment_compute():
    form = SentimentForm()
    fname = session["cur_data_dir"] + "/" + "fig_sentiment.txt"
    if os.path.isfile(fname):
        with open(fname) as f:
            fig = f.read()
        return render_template('sentiment_page.html',
                            fig = fig,
                            form=form,
                             )
    
    df_path = session["cur_data_dir"] + "/" + "tweets_collected.csv"
    fig = sentiment_main(df_path, session["lang"])
    with open(fname, "w") as f:
        f.write(fig)
    return render_template('sentiment_page.html',
                            fig = fig,
                            form=form,
                             )

@app.route('/correlation', methods=['GET', 'POST'])
def correlation_page():
    form = TargetWordsForm()
    if request.method=="POST":
        if form.validate_on_submit:
            session['target_words'] = form.target_words.data
            session['word_count2keep'] = form.word_count2keep.data
            return redirect(url_for('target_correlation'))

    if form.errors != {}: #If there are not errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')
      

    return render_template('correlation_page.html', 
                                form=form)

@app.route('/correlation_compute', methods=['GET', 'POST'])
def correlation_compute():
    form = TargetWordsForm()
    
    if request.method=="POST":
        if form.validate_on_submit:
            session['target_words'] = form.target_words.data
            session['word_count2keep'] = form.word_count2keep.data
            return redirect(url_for('target_correlation'))
    
    x = "_" + "_".join(session['target_words'].split(",")) + "_"
    fname = session["cur_data_dir"] + "/" + "fig_correlation" + x +str(session['word_count2keep'])  + ".txt"

    if os.path.isfile(fname):
        with open(fname) as f:
            fig = f.read()
        return render_template('correlation_page.html',
                                fig = fig,
                                form=form,
                                )
    
    df_path = session["cur_data_dir"] + "/" + "tweets_collected.csv"
    target_words = session['target_words'] 
    word_count2keep = session['word_count2keep']
    target_words = target_words.split(",")
    fig, df_tweets = correlation_main(model_ser_encoder, df_path, target_words, word_count2keep)
    
    current_dir = session["cur_data_dir"]
    df_tweets.to_csv(current_dir + "/" + "tweets_collected.csv", index=False)
    
    with open(fname, "w") as f:
        f.write(fig)

    return render_template('correlation_page.html',
                            fig = fig,
                            form=form,
                            )

@app.route('/', methods=['GET', 'POST'])
def index_page():
    return render_template('index_page.html')

@app.route('/search', methods=['GET', 'POST'])
def search_page():       
    form = SearchInputForm()
    if form.validate_on_submit():
        session['search_text'] = (form.search_text.data)
        session['startdate'] = str(form.startdate.data)
        session['enddate'] = str(form.enddate.data)
        session['lang'] = str(form.lang.data)
        session['max_tweets'] = (form.max_tweets.data)

        try:
            remove_old_directories("./twan/data/")
        except Exception as err_msg:
            print(err_msg)

        session["cur_data_dir"] = "./twan/data/" + random_key(10)
        
        return redirect(url_for('target'))
        
    if form.errors != {}: #If there are not errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')
        
    return render_template('search_page.html', 
                                form=form)

@app.route('/plots')
def plot_page():
    
    tw = TWAN(session['search_text'], 
                    session['startdate'], 
                    session['enddate'], 
                    session['lang'], 
                    session['max_tweets'])  

    if os.path.isdir(session["cur_data_dir"]):
        current_dir = session["cur_data_dir"]
        tw = read_plot_data(tw, current_dir)
        return render_template('plots_page.html',
                            tw = tw,
                            )


    tw.collect_tweets()
    os.makedirs(session["cur_data_dir"]) 
    current_dir = session["cur_data_dir"]
    tw.df.to_csv(current_dir + "/" + "tweets_collected.csv", index=False)
    try:
        tw.hourly()
        tw.daily()
        tw.tweet_count_per_hour()
        tw.tweet_count_per_day()
        tw.wordcloud_func()
        save_tw(current_dir, tw)
        
        searchdate_now = datetime.utcnow()
        # this is for mysql
        # searchdate_now = searchdate_now.strftime('%Y%m%d%H%M%S%f')
        search1 = searchitems(search_text=session['search_text'],
                                startdate=datetime.strptime(session['startdate'], "%Y-%m-%d"),
                                enddate=datetime.strptime(session['enddate'], "%Y-%m-%d"),
                                lang=session['lang'],
                                searchdate = searchdate_now,
                                data_length = tw.tw_count)

        try:
            db.session.add(search1)
            db.session.commit()
            item = searchitems.query.filter_by(searchdate = searchdate_now).first()
            session["search_id"] = item.id
            # print('------------session["search_id"]------------------', session["search_id"])
        except Exception as ex:
            print("------------------------------\n", ex)
            print("------------------------------")

    except:
        flash(f'There is no tweet in this search criteria!', category='danger')
        return render_template('plots_page.html')    
    

    return render_template('plots_page.html',
                            tw = tw,
                            )

@app.route('/tweets')
def tweets_page():
    tweets = pd.read_csv(session["cur_data_dir"] + "/" + "tweets_collected.csv")
    return render_template('tweets_page.html',
                            tweets = tweets)

@app.route("/target_endpoint")
def target():
    return render_template('loading.html')

@app.route("/target_word_cooc")
def target_word_cooc():
    return render_template('loading_word_cooc.html')

@app.route("/target_correlation")
def target_correlation():
    return render_template('loading_correlation.html')

@app.route("/target_sentiment")
def target_sentiment():
    return render_template('loading_sentiment.html')

@app.route("/contact")
def contact_page():
    return render_template('contact_page.html')

