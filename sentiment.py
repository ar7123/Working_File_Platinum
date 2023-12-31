from flask import Flask, jsonify
from flask import request
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flasgger import swag_from
import matplotlib.pyplot as plt
import seaborn as sns
import tensorflow as tf
import pickle
import numpy as np
import sklearn
import pandas as pd
import re
import emoji
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from tensorflow.keras.preprocessing.text import Tokenizer
from keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

#Flask and Swagger endpoint
sentiment_app = Flask(__name__)
sentiment_app.json_provider_class = LazyJSONEncoder
swagger_template = dict(
    info = {
        'title' : LazyString(lambda: 'Sentiment Analysis'),
        'version' : LazyString(lambda: '1.0.0'),
        'description' : LazyString(lambda: 'Dokumentasi API Sentiment Analysis dengan model Neural Network dan LTSM')
    },
    host = LazyString(lambda: request.host)
)

swagger_config = {
    'headers': [],
    'specs': [
        {
            'endpoint': 'docs',
            'route': '/docs.json',
        }
    ],
    'static_url_path': '/flasgger_static',
    'swagger_ui': True,
    'specs_route': '/docs/'
}
swagger = Swagger(sentiment_app, template=swagger_template,             
                  config=swagger_config)


# Homepage route
@sentiment_app.route('/')
def homepage():
    return render_template('homepage.html')

#Tools to run the function 
max_features = 100000
sentiment = ['negative', 'neutral', 'positive']
tokenizer = Tokenizer(num_words=max_features, split=' ', lower=True)
#===================================================================
#Vectorizing For Neural Network
#count_vect = pickle.load(open('resources_nn/mockup.pkl','rb'))
count_vect = 'resources_nn/mockup.pkl'
with open(count_vect, 'rb') as file:
    file_data = pickle.load(file)

#Load Model for Neural Network
model_NN = load_model('resources_nn/model.h5')
#===================================================================
#Load Feature Extraction for LSTM
file = pickle.load(open('resources_lstm/mockup.pkl','rb'))

#Load Model for LSTM
model_LSTM = load_model('resources_lstm/model.h5')
#===================================================================              

#Func API Neural Network (text)
@swag_from('docs/NN_text.yml', methods=['POST'])
@sentiment_app.route('/NN_text', methods=['POST'])
def NN_text():
    #Request text 
    original_text = request.form.get('text')
    #Cleansing text
    clean_text = [cleansing(original_text)]
    #Vectorizing 
    text = count_vect.transform(clean_text)
    #Predict sentiment
    result = model_NN.predict(text)[0]

    json_response = {
        'status_code': 200,
        'description': 'Result of Sentiment Analysis using Neural Network',
        'data' : {
            'text' : original_text,
            'sentiment' : result 
        },
    }

    response_data = jsonify(json_response)
    return response_data

#===================================================================
#Func API for Neural Netwrok(File)
@swag_from('docs/NN_file.yml', methods=['POST'])
@sentiment_app.route('/NN_file', methods=['POST'])
def NN_file():
    #upload file
    file = request.files['file']
    #Import file to pandas DataFrame
    df = pd.read_csv(file,header=0)
    #Cleansing text
    df['text_clean'] = df.apply(lambda row : cleansing(row['text']), axis = 1)

    result = []
    #Vectorizing & Predict sentiment
    for index, row in df.iterrows():
        text = count_vect.transform([(row['text_clean'])])

        #append predicted sentiment to result 
        result.append(model_NN.predict(text)[0])
        
    # Get result from file in "List" format
    original_text = df.text_clean.to_list()

    json_response = {
        'status_code': 200,
        'description': 'Result of Sentiment Analysis using Neural Network',
        'data': {
            'text' : original_text,
            'sentiment' : result
        },
    }

    response_data = jsonify(json_response)
    return response_data


#==================================================================

#Func API LSTM(Text)
@swag_from('docs/LSTM_text.yml',methods=['POST'])
@sentiment_app.route('/LSTM_text',methods=['POST'])
def LSTM_text():
    #Request text 
    original_text = request.form.get('text')
    #Cleansing
    text = [cleansing(original_text)]
    
    #Feature Extraction
    feature = tokenizer.texts_to_sequences(text)
    feature = pad_sequences(feature, maxlen=feature_file_from_lstm.shape[1])
    
    #Prediction
    prediction = model_LSTM.predict(feature)
    get_sentiment = sentiment[np.argmax(prediction[0])]
    json_response = {
      'status_code' : 200,
        'description' : 'Result of Sentiment Analysis using LSTM',
        'data' : {
            'text' : original_text,
            'sentiment' : get_sentiment
        },
    }
    response_data = jsonify(json_response)
    return response_data

#===================================================================

#Func API LSTM(File)
@swag_from('docs/LSTM_file.yml',methods=['POST'])
@sentiment_app.route('/LSTM_file',methods=['POST'])
def LSTM_file():
    # Upladed file
    file = request.files['file']

    # Import file csv ke Pandas
    df = pd.read_csv(file,header=0)
    #Cleansing
    df['text_clean'] = df.apply(lambda row : cleansing(row['text']), axis = 1)
    
    result = []

    # Feature Extraction & Predict Data
    for index, row in df.iterrows():
        text = tokenizer.texts_to_sequences([(row['text_clean'])])
        feature = pad_sequences(text, maxlen=feature_file_from_lstm.shape[1])
        prediction = model_LSTM.predict(feature)
        #predict the sentiment 
        get_sentiment = sentiment[np.argmax(prediction[0])]
        # append sentiment to result
        result.append(get_sentiment)

    # Get result from file in "List" format
    original = df.text_clean.to_list()

    json_response = {
        'status_code' : 200,
        'description' : 'Result of Sentiment Analysis from csv file using LSTM',
        'data' : {
            'text' : original,
            'sentiment' : result
        },
    }

    response_data = jsonify(json_response)
    return response_data

#===================================================================
#Run API 
if __name__ == '__main__' :
    sentiment_app.run(debug=True)
