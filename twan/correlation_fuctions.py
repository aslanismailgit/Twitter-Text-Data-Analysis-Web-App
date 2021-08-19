#%%
import pandas as pd
import numpy as np 
import base64
from io import BytesIO
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from twan.functions import cleaner
from twan import model_ser_encoder
# if embeddings are taken from gcp ai platform use this function
# also fix init file
# from twan.gcp_functions import embeddings_from_gcp 

from sklearn.metrics.pairwise import cosine_similarity

# model_encoder can also be imported here,
# but importing at the init makes it one time
# import tensorflow as tf
# import tensorflow_hub as hub
# import tensorflow_text as text

# print("Version: ", tf.__version__)
# print("GPU is", "available" if tf.config.list_physical_devices('GPU') else "NOT AVAILABLE")

#%%
# def correlation_main(df_path, target_words, word_count2keep):
def correlation_main(model_ser_encoder, df_path, target_words, word_count2keep):
    # this part is moved to init
    # model_link = "https://tfhub.dev/google/universal-sentence-encoder-multilingual/3"
    # saved_model_link = "./twan/tf_model/"
    # # model_ser_encoder = hub.load(model_link)
    # model_ser_encoder = hub.load(saved_model_link)

    # model_ser_encoder = tf.saved_model.load(saved_model_link)
    # print("--------- model imported -------")

    df = pd.read_csv( df_path)
    df["Datetime"] = pd.to_datetime(df["Datetime"])
    if "Cleantext" not in df.columns:
        df["Cleantext"] = df['Text'].apply(cleaner)
    daily_tws = (df.groupby(pd.Grouper(key='Datetime', freq='1d', convention='start')))
    
    # target_word_embed = embeddings_from_gcp(target_words)
    # print("Embeddings taken from GCP ------->:", target_word_embed.shape)
    print("model_ser_encoder ------->:", model_ser_encoder)
    target_word_embed = model_ser_encoder(target_words)
    print(target_word_embed)
    df_scores = get_df_scores(daily_tws, target_word_embed, target_words, model_ser_encoder, word_count2keep)
    # df_scores = get_df_scores(daily_tws, target_word_embed, target_words, word_count2keep)
    fig = plot_correlation(df_scores)
    return fig, df

# fig, df = correlation_main(df_path, model_ser_encoder, target_words, word_count2keep)
#%% daily freq
from wordcloud import STOPWORDS
import wordcloud

def get_word_freq(corpus):
    wc = wordcloud.WordCloud(background_color="white", 
                            max_words=100, width=400, height=400, 
                            collocations=False, random_state=1, stopwords=STOPWORDS)
    wc.generate(corpus)
    text_dictionary = wc.process_text(corpus)

    word_freq={k: v for k, v in sorted(text_dictionary.items(),reverse=True, key=lambda item: item[1])}

    df_freq = pd.DataFrame(index = word_freq.keys(), data=word_freq.values()).reset_index()
    df_freq.columns = ["Word", "Count"]
    df_freq["Frequency"] = df_freq.Count / np.sum(df_freq.Count) 
    return df_freq

#%%
def get_mean_score(embeddings_, target_word_embed):
    cos_sim = cosine_similarity(embeddings_, target_word_embed)
    cos_sim.shape
    arccos = np.arccos(cos_sim)
    # arccos = arccos[np.logical_not(np.isnan(arccos))]
    arccos[(np.isnan(arccos))] = np.nanmean(arccos)
    arccos = np.reshape(arccos,(-1,len(target_word_embed)))
    sim = 1 - arccos/np.pi
    mean_sim = np.mean(sim,axis=0)
    return mean_sim

def get_df_scores(daily_tws, target_word_embed, target_words, model_ser_encoder, word_count2keep):
# def get_df_scores(daily_tws, target_word_embed, target_words, word_count2keep):
    df_scores = pd.DataFrame(columns=target_words)
    for i,j in daily_tws:
        print("\n-----------", i)
        try:
            df_temp = daily_tws.get_group(i)
            print(df_temp.shape)
        except:
            df_temp = pd.DataFrame()
        if df_temp.shape[0]==0:
            a = np.empty((1,len(target_word_embed)))
            a[:] = np.nan
            df_scores.loc[i,:] = a
            continue
        corpus = ' '.join(df_temp["Cleantext"])
        print(len(corpus))
        df_freq = get_word_freq(corpus)
        print(df_freq.shape)
        top_n_words = df_freq["Word"][:word_count2keep]
        embeddings_ = model_ser_encoder(top_n_words)
        # embeddings_ = embeddings_from_gcp(top_n_words)
        mean_sim = get_mean_score(embeddings_, target_word_embed)
        print(mean_sim)
        df_scores.loc[i,:] = mean_sim
    return df_scores
# get_df_scores(daily_tws, target_word_embed, target_words, model_ser_encoder, word_count2keep)
#%%
def plot_correlation(df_scores):
    fig = Figure(figsize=(12,6))
    ax = fig.subplots()
    x = df_scores.index
    for col in df_scores.columns:
        ax.plot(x, df_scores[col],  marker='.', label=col)

    ax.set_ylabel('Tweet Scores')
    ax.set_xlabel('Date')
    ax.set_title(f"Daily Mean Tweet Correlation")
    ax.grid(True)
    ax.legend()
    buf = BytesIO()
    fig.savefig(buf, format="png")
    return base64.b64encode(buf.getbuffer()).decode("ascii")

# fig = correlation_main(df_path, target_words, word_count2keep)
