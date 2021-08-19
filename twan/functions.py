#%%
import snscrape.modules.twitter as sntwitter
import pandas as pd
import numpy as np
import time
import base64
from io import BytesIO
from matplotlib.figure import Figure
import wordcloud
from wordcloud import STOPWORDS
import os

from twan import mail
from flask_mail import Message

import random
import string
from PIL import Image
import io
from shutil import copyfile, make_archive, rmtree

#%%
class TWAN: 
    def __init__(self, search_term_input, start_time, end_time, lang, max_tweets):
        self.search_term_input = search_term_input
        self.start_time = start_time
        self.end_time = end_time
        self.lang = lang
        self.max_tweets = max_tweets
        print("initialized")

    def collect_tweets(self):
        self.search_term = f"{self.search_term_input} lang:{self.lang} since:{self.start_time} until:{self.end_time}"
        tweets_list_temp = []
        sns_tw = sntwitter.TwitterSearchScraper(self.search_term).get_items()
        for i,tweet in enumerate(sns_tw):
            if i>self.max_tweets:
                break
            if i%50 == 0:
                print("-----", i, tweet.date)
            tweets_list_temp.append([tweet.date, tweet.id, tweet.content, tweet.username])
        df = pd.DataFrame(tweets_list_temp, columns=['Datetime', 'Tweet Id', 'Text', 'Username'])
        
        
        df["Datetime"] = pd.to_datetime(df["Datetime"])
        df['Text'] = df['Text'].astype('str')
        df.dropna(axis=0, inplace=True)
        df["Day"] = df["Datetime"].apply(lambda x: x.day)
        df["Weekday"] = df["Datetime"].apply(lambda x: x.weekday())
        df["Hour"] = df["Datetime"].apply(lambda x: x.hour)
        self.df = df
        self.tw_count = len(df)
        # print(self.search_term)
    
    def tweet_count_per_day(self):
        daily_tw_count = pd.DataFrame(self.df.groupby(pd.Grouper(key='Datetime', freq='1d', convention='start')).size())
        daily_tw_count.columns = ["Count"]
        fig = Figure(figsize=(12,6))
        ax = fig.subplots()
        ax.plot(daily_tw_count.index, daily_tw_count.Count)
        ax.set_ylabel('Tweet Count')
        ax.set_xlabel('Date')
        ax.set_title(f"Tweet Count Per Day")
        buf = BytesIO()
        fig.savefig(buf, format="png")
        self.tw_count_per_day = base64.b64encode(buf.getbuffer()).decode("ascii")
    
    def tweet_count_per_hour(self):
        daily_tw_count = pd.DataFrame(self.df.groupby(pd.Grouper(key='Datetime', freq='1h', convention='start')).size())
        daily_tw_count.columns = ["Count"]
        fig = Figure(figsize=(12,6))
        ax = fig.subplots()
        ax.plot(daily_tw_count.index, daily_tw_count.Count)
        ax.set_ylabel('Tweet Count')
        ax.set_xlabel('Date')
        ax.set_title(f"Tweet Count Per Hour")
        buf = BytesIO()
        fig.savefig(buf, format="png")
        self.tw_count_per_hour = base64.b64encode(buf.getbuffer()).decode("ascii")
        
    def hourly(self):
        fig = Figure(figsize=(12,6))
        ax = fig.subplots()
        ax.hist(self.df["Hour"].values, bins=24)
        ax.set_ylabel('Tweet Count')
        ax.set_xlabel('Date')
        ax.set_title(f"Hourly Tweet Counts")
        buf = BytesIO()
        fig.savefig(buf, format="png")
        self.hourly_data = base64.b64encode(buf.getbuffer()).decode("ascii")
    
    def daily(self):
        fig = Figure(figsize=(12,6))
        ax = fig.subplots()
        ax.hist(self.df["Day"].values, bins=24)
        ax.set_ylabel('Tweet Count')
        ax.set_xlabel('Date')
        ax.set_title(f"Daily Tweet Counts")
        buf = BytesIO()
        fig.savefig(buf, format="png")
        self.daily_data = base64.b64encode(buf.getbuffer()).decode("ascii")

    def wordcloud_func(self):
        corpus = ' '.join(self.df["Text"])
        if self.lang == "tr":
            tr_stopwords = pd.read_csv("./twan/static/tr_stopwords.txt", header=None).values
            stopwords = np.squeeze(tr_stopwords)
        
        elif self.lang == "en":
            stopwords = STOPWORDS
            stopwords.update(["https", "co", "t", "s", "u", "will", "m"])

        wc = wordcloud.WordCloud(background_color="white", 
                            max_words=300, width=800, height=400, 
                            collocations=False, random_state=1, stopwords=stopwords)
        wc.generate(corpus)
        fig = Figure(figsize=(12,6))
        ax = fig.subplots()
        ax.imshow(wc, interpolation='bilinear')
        ax.axis("off")
        buf = BytesIO()
        fig.savefig(buf, format="png")
        self.wc = base64.b64encode(buf.getbuffer()).decode("ascii")

        text_dictionary = wc.process_text(corpus)
   
        word_freq={k: v for k, v in sorted(text_dictionary.items(),reverse=True, key=lambda item: item[1])}

        df_freq = pd.DataFrame(index = word_freq.keys(), data=word_freq.values()).reset_index()
        df_freq.columns = ["Word", "Count"]
        df_freq["Frequency"] = df_freq.Count / np.sum(df_freq.Count) 
        ordered_word_freq = dict(sorted(text_dictionary.items(), key=lambda item: -item[1]))

        self.word_freq = word_freq
        self.df_freq = df_freq
        self.ordered_word_freq = ordered_word_freq

# %%
import emoji
import re
def cleaner(tweet):
    tweet = tweet.lower()
    tweet = re.sub(r'\w+:\/\/\S+', ' ', tweet)
    tweet = re.sub(r"(?:\@|http?\://|https?\://)\S+", "", tweet)
    # tweet = re.sub(r"(?:\www?)\S+", "", tweet)
    tweet = re.sub(r'#\w+ ?', '', tweet)
    tweet = re.sub(r'[^\w\s]','', tweet)
    tweet = " ".join(tweet.split())
    tweet = ''.join(c for c in tweet if c not in emoji.UNICODE_EMOJI)
    return tweet
#%%
def send_email(recipients, link):
    msgbody = "Hey, you can reach the analysis results by following below link"
    sender = 'twittranalysis@gmail.com'
    msg = Message(msgbody, 
                sender = ("Twitter Data Analysis TWAN",   sender),
                recipients = [recipients])
    msg.body = "Hey, you can reach the analysis results by following below link"
    msg.html = f'<b>Hey,</b> <b>you can reach the analysis results by following this link </b><a href="{link}">Download TWAN Analysis Reports</a>'
    mail.send(msg)

#%%
def save_as_png(fname, current_dir, zip_path):
    with open(current_dir + "/" + fname ) as f:
        fig_base = f.read()
    image = base64.b64decode(str(fig_base))       
    img = Image.open(io.BytesIO(image))
    imagePath = zip_path + "/" + fname.split(".")[0] + ".png"
    img.save(imagePath)

def copy2zip(current_dir):
    zip_dir_name = current_dir.split("/")[-1]
    fnames = os.listdir(current_dir)
    zip_path = current_dir + "/" +"zipdir"
    if not os.path.exists(zip_path):
        os.makedirs(zip_path)
    for fname in fnames:
        if ".csv" in fname:
            src = current_dir + "/" + fname
            dst = zip_path + "/" + fname
            copyfile(src, dst)
        elif ".txt" in fname:
            save_as_png(fname, current_dir, zip_path)
    zip_dir_name = "twan_" + zip_dir_name
    make_archive(current_dir + "/" + zip_dir_name, 'zip', zip_path)
    return zip_dir_name

def read_plot_data(tw, current_dir):
    tw.df_freq = pd.read_csv(current_dir + "/" +"df_freq.csv")
    npfilename =  current_dir + "/" +"tw_count.npy"
    tw.tw_count = np.load(npfilename).tolist()
    with open(current_dir + "/" +'daily_data.txt') as f:
        tw.daily_data = f.read()
    with open(current_dir + "/" +'hourly_data.txt') as f:
        tw.hourly_data = f.read()
    with open(current_dir + "/" +'tw_count_per_day.txt') as f:
        tw.tw_count_per_day = f.read()
    with open(current_dir + "/" +'tw_count_per_hour.txt') as f:
        tw.tw_count_per_hour = f.read()
    with open(current_dir + "/" +'wc.txt') as f:
        tw.wc = f.read()
    return tw
#%%
def save_tw(current_dir, tw):
    files2save = [
        "tw_count_per_day",
        "tw_count_per_hour",
        "hourly_data",
        "daily_data",
        "wc",
        ]
    
    for d in files2save:
        fname = current_dir + "/" + d + ".txt"
        savebuf(fname, eval(f"tw.{d}"))
    fname = current_dir + "/" + "df_freq.csv"
    npfilename =  current_dir + "/" +"tw_count.npy"
    np.save(npfilename, tw.tw_count)
    tw.df_freq.to_csv(fname, index=False)
#%%
def savebuf(fname, data):
    with open(fname, "w") as f:
        f.write(data)
#%%
def random_key(n):
    letters = string.ascii_lowercase
    key = ''.join(random.choice(letters) for i in range(10)) #+ ".csv"
    return key

def remove_old_files(path):
    now = time.time()
    for filename in os.listdir(path):
        if ".csv" not in filename:
            continue
        if "sample" in filename:
            continue
        if "lljjjjwief" in filename:
            continue
        filestamp = os.stat(os.path.join(path, filename)).st_mtime
        filecompare = now - 5 * 60 # del files created 5 minutes ago
        if  filestamp < filecompare:
            os.remove(path+filename)

def remove_old_directories(path):
    now = time.time()
    for dirname in os.listdir(path):
        if "keep" in dirname:
            continue
        filestamp = os.stat(os.path.join(path, dirname)).st_mtime
        filecompare = now - 1 * 60 # del files created 1 minutes ago
        if  filestamp < filecompare:
            rmtree(path+dirname)
#%%


