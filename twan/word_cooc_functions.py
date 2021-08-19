#%%
import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import base64
from io import BytesIO

import seaborn as sns
from matplotlib.figure import Figure

from twan.functions import cleaner


#%%
def word_cooc_main(path, top_n_words):
    df_tweets = pd.read_csv(path + "tweets_collected.csv")
    print(df_tweets.columns)
    if "Cleantext" not in df_tweets.columns:
        df_tweets["Cleantext"] = df_tweets['Text'].apply(cleaner)
        print(df_tweets.columns)
    df_freqs = pd.read_csv(path + "df_freq.csv")
    print(df_tweets.shape, df_freqs.shape)
    feats = df_freqs.Word[:top_n_words] 
    print("len(feats)----------", len(feats))
    corr = word_cooc_corr(df_tweets, feats)
    fig = word_cooc_fig(corr, feats)
    return fig, df_tweets
# fig, df_tweets = word_cooc_main(path, top_n_words)


#%%
def word_cooc_corr(df_tweets, feats):
    corpus = df_tweets.Text
    print("corpus-----", len(corpus))
    X = np.zeros((len(corpus),len(feats)))

    for j, w in enumerate(feats):
        for i,t in enumerate(corpus):
            if t==t:
                if (w in t):
                    X[i,j]=1
    
    corr = np.corrcoef(X.T)
    return corr
# corr = word_cooc_corr(df_tweets, column_filters)
#%%
def word_cooc_fig(corr, feats):
    sns.set(font_scale=1.2)
    fig = Figure(figsize=(12,8))
    ax = fig.subplots()
    hm = sns.heatmap(
        corr,
        xticklabels=feats,
        yticklabels=feats,
        vmin=-1,
        vmax=1,
        cmap="YlOrRd", ax=ax)
    ax.set_xticklabels(feats, rotation=90)
    ax.set_yticklabels(feats, rotation=0)
    ax.set_title("Word Co-occurence")
    buf = BytesIO()
    fig = hm.get_figure() 
    fig.savefig(buf, format="png")
    return base64.b64encode(buf.getbuffer()).decode("ascii")

