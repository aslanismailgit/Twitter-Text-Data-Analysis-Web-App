#%%
import pandas as pd
import numpy as np 
import base64
from io import BytesIO
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from transformers import pipeline
from transformers import AutoTokenizer, TFAutoModelForSequenceClassification
from twan.functions import cleaner
#%%
def sentiment_main(df_path, lang):
    classifier = get_classifier(lang)
    df = pd.read_csv(df_path)
    df["Datetime"] = pd.to_datetime(df["Datetime"])
    if "Cleantext" not in df.columns:
        df["Cleantext"] = df['Text'].apply(cleaner)
    daily_tws = (df.groupby(pd.Grouper(key='Datetime', freq='1d', convention='start')))
    df_sent_score = get_sent_scores(daily_tws, classifier, lang)
    fig = plot_correlation(df_sent_score, lang)
    return fig

# %%
def get_classifier(lang):
    if lang == "tr":
        model_path = './twan/transformers_tr/'
        print("-----tr-----", lang)
    else:
        model_path = './twan/transformers/' 
        print("-----else-----", lang)
    model = TFAutoModelForSequenceClassification.from_pretrained(model_path, local_files_only=True)
    print("----------- transformer model loaded ------------")
    tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
    print("----------- transformer tokenizer loaded ------------")
    classifier = pipeline('sentiment-analysis', model=model, tokenizer=tokenizer)
    # classifier(["brilliant"])
    # This part to is to download the model and use from ./cache/
    # do not forget to install pytorch if you use this part !!!
    # model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
    # model = TFAutoModelForSequenceClassification.from_pretrained(model_name, from_pt=True)
    # tokenizer = AutoTokenizer.from_pretrained(model_name)
    # classifier = pipeline('sentiment-analysis', model=model, tokenizer=tokenizer)
    # model_path = 'my_model_dir'
    # classifier.save_pretrained(model_path)
    return classifier
# %%
def get_sent_scores(daily_tws, classifier, lang):
    df_sent_score = pd.DataFrame(columns=["mean_score", "weighted_score"])
    for i,_ in daily_tws:
        print("\n-----------", i)
        try:
            df_temp = daily_tws.get_group(i)
            if df_temp.shape[0]>100:
                df_temp = df_temp.sample(n=100)
            print(df_temp.shape)
        except:
            df_temp = pd.DataFrame()
        if df_temp.shape[0]==0:
            a = np.empty((1,2))
            a[:] = np.nan
            df_sent_score.loc[i,:] = a
            continue
        results = classifier(df_temp["Cleantext"].tolist())
        results = pd.DataFrame(results)
        print(results.shape)
        if lang == "tr":
            results["label_numberic"] = results["label"].apply(lambda x: -1 if x=="negative" else 1)
            results["score_with_direction"] = results["label_numberic"] * results["score"]
            mean_score = results["score_with_direction"].mean()
            weighted_score = np.nan
        else:
            results["LabelScore"] = results['label'].apply(lambda x: x.split(" ")[0]).astype("int")
            mean_score = results["LabelScore"].mean()
            weighted_score = (results["LabelScore"] * results["score"]).mean()
        print(mean_score, weighted_score)
        df_sent_score.loc[i,:] = [mean_score, weighted_score]
    return df_sent_score
# get_sent_scores(daily_tws, classifier)
# %%
def plot_correlation(df_sent_score, lang):
    if lang=="tr":
        title = f"Daily Mean Tweet Sentiment Score : Range -1 and 1"
        y0 = -1.05
        y1 = 1.05
    else:
        title = f"Daily Mean Tweet Sentiment Score : Range 0 and 5"
        y0 = 0
        y1 = 5.00

    fig = Figure(figsize=(12,6))
    ax = fig.subplots()
    x = df_sent_score.index
    for col in df_sent_score.columns:
        ax.plot(x, df_sent_score[col],  marker='.', label=col)
        if lang == "tr": break #no weight score for turkish

    ax.set_ylabel('Sentiment Scores')
    ax.set_xlabel('Date')
    ax.set_title(title)
    ax.grid(True)
    ax.legend()
    ax.set_ylim(y0, y1)
    buf = BytesIO()
    fig.savefig(buf, format="png")
    return base64.b64encode(buf.getbuffer()).decode("ascii")
# %%
