from flask import Flask, render_template, request
import json
import pickle
import numpy as np
import pandas as pd
import string
import random
from tensorflow import keras
from keras.models import model_from_json
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from thefuzz import fuzz

# inisiasi sastrawi Bahasa Indonesia
factory = StemmerFactory()
stemmer = factory.create_stemmer()

with open('deploy_dataset.json', 'r') as f:
    dataset = json.load(f)

df = pd.DataFrame(dataset)

with open('list_pertanyaan.json', 'r') as f:
    list_pertanyaan = json.load(f)

list_pertanyaan = pd.DataFrame(list_pertanyaan)

with open('combined_stop_words.txt') as file:
    stop_words = set(file.read().split())

with open('tekkom_dict.txt') as file:
    tekkom_dict = eval(file.read())

# Import Word Index
with open('word_index.pickle', 'rb') as handle:
    word_index = pickle.load(handle)

# Load Model
json_file = open('model_90persen_split15_8421.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
model = model_from_json(loaded_model_json)

# Load Weights dari Model
model.load_weights("model_90persen_split15_8421.h5")


def remove_stop_words(text):
    words = text.split()
    filtered_words = []
    for word in words:
        if word.lower() not in stop_words:
            filtered_words.append(word)
    return ' '.join(filtered_words)


def convert_tekkom_words(text):
    words = text.split()
    converted_words = []
    for word in words:
        if word.lower() in tekkom_dict:
            converted_words.append(tekkom_dict[word.lower()])
        else:
            converted_words.append(word)
    return ' '.join(converted_words)


def preprocess_text(text):

    text = str(text)
    text = text.lower()
    text = text.translate(str.maketrans(
        dict.fromkeys(string.punctuation, ' ')))

    text = convert_tekkom_words(text)
    text = stemmer.stem(text)

    text = remove_stop_words(text)

    return text


# Function untuk mendapatkan label
def predict_intent(text):
    tokenizer = keras.preprocessing.text.Tokenizer(num_words=len(word_index))
    tokenizer.word_index = word_index
    sequence = tokenizer.texts_to_sequences([preprocess_text(text)])
    sequence = keras.preprocessing.sequence.pad_sequences(sequence, maxlen=25)
    prediction = model.predict(sequence, verbose=0)[0]
    prediction = np.argmax(prediction)
    intent = df["label"].unique()[prediction]
    return intent


def getLabel(text):
    preproc = preprocess_text(text)
    predict = predict_intent(preproc)

    return predict


def getAnswerComb(text, label):
    text = preprocess_text(text)
    qnaPair = df[df["label"] == label].reset_index(drop=True)
    tempPertanyaan = qnaPair["pertanyaan"].apply(preprocess_text).tolist()

    index = 0
    tempHasil = []
    tempRatio = 0
    for pertanyaan in tempPertanyaan:
        tokens1 = set(text.split())
        tokens2 = set(pertanyaan.split())
        similar_tokens = tokens1.intersection(tokens2)

        # token_based = len(similar_tokens)
        token_based = int(100*(len(similar_tokens) /
                          (len(tokens1) + len(tokens2) - len(similar_tokens))))

        if token_based >= tempRatio:
            tempRatio = token_based
            tempHasil.append((pertanyaan, token_based, index))
            tempHasil = sorted(tempHasil, key=lambda x: x[1], reverse=True)

        if len(tempHasil) > 5:
            del tempHasil[-1]

        index += 1

    tempHasil = sorted(tempHasil, key=lambda x: x[1], reverse=True)
    fuzzRatio = 0
    for i in range(len(tempHasil)):
        fuzzy_token_ratio = fuzz.token_set_ratio(text, tempHasil[i][0])
        if fuzzy_token_ratio > fuzzRatio:
            bestSimilarity = tempHasil[i][0]
            index = tempHasil[i][2]
            fuzzRatio = fuzzy_token_ratio

    bestSimilarity = qnaPair["pertanyaan"][index]
    ratio = fuzzRatio
    bestAnswer = qnaPair["jawaban"][index]

    answered = [bestSimilarity, ratio, bestAnswer, index]
    return answered


def answerWithLabelClassification(text):
    labelTerprediksi = getLabel(text)
    pertanyaanTerprediksi, rasio, jawabanTerprediksi, index = getAnswerComb(
        text, labelTerprediksi)

    answered = [index, pertanyaanTerprediksi,
                labelTerprediksi, jawabanTerprediksi, rasio]
    return answered


def bot_response(nama, text):
    nama = nama.lower()
    answer = answerWithLabelClassification(text)

    hasil = f"<b>Pertanyaan Terprediksi:</b><br>{answer[1]}<br><br><b>Jawaban:</b><br>{answer[3]}"

    return hasil


label_dict = {}
for i, element in enumerate(df["label"].unique()):
    label_dict[element] = i
reversed_dict = {v: k for k, v in label_dict.items()}

# ===========================================================================================#
# FLASK #


app = Flask(__name__)
app.static_folder = 'static'


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/post")
def get_bot_response():
    nama = request.args.get('nama')
    userText = request.args.get('msg')

    if (userText.lower() == "tidak" 
        or userText.lower() == "gak" 
        or userText.lower()  == "g"
        or userText.lower() == "ga"):
        
        return f"Terima kasih telah menggunakan chatbot"


    return bot_response(nama, userText)


if __name__ == "__main__":
    app.run(debug=True)
