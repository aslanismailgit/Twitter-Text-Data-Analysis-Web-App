#%%
import os
import numpy as np 
import requests
import googleapiclient.discovery
from google.api_core.client_options import ClientOptions
#%%
# this function is required if the embeddings are taken from 
# TF USE model is deployed to gcp ai platform
#%%
def embeddings_from_gcp(target_words):
    # this is the wrapper function of predictions function
    # Google Cloud Services look for these when your app runs
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./twan/practical-bebop-322707-de7214c50a96.json"
    PROJECT = "practical-bebop-322707"
    MODEL_NAME="ai_tf_model"
    VERSION_NAME="V001"
    REGION="us-central1"
    return predictions_from_gcp(target_words, PROJECT, REGION, MODEL_NAME, VERSION_NAME)
#%%
def predictions_from_gcp(target_words, project, region, model, version=None):
    #%% Create the ML Engine service object
    prefix = "{}-ml".format(region) if region else "ml"
    api_endpoint = "https://{}.googleapis.com".format(prefix)
    client_options = ClientOptions(api_endpoint=api_endpoint)

    # Setup model path
    model_path = "projects/{}/models/{}".format(project, model)
    version = "V001"
    if version is not None:
        model_path += "/versions/{}".format(version)

    # Create ML engine resource endpoint and input data
    ml_resource = googleapiclient.discovery.build(
        "ml", "v1", cache_discovery=False, client_options=client_options).projects()

    # target_words = ["good", "bad"]
    input_data_json = {"instances": target_words}

    request = ml_resource.predict(name=model_path, body=input_data_json)
    #%%
    response = request.execute()

    if "error" in response:
        raise RuntimeError(response["error"])

    return np.array(response["predictions"])

