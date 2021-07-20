import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # or any {'0', '1', '2'}

import random
import json
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.layers import Dense, Activation, Dropout 
from tensorflow.keras.models import Sequential
from tensorflow.keras.models import load_model
import numpy as np
import pickle

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

import nltk
nltk.data.path.append(os.path.join(BASE_DIR,'data/punkt'))
nltk.data.path.append(os.path.join(BASE_DIR,'data/wordnet'))
nltk.download('punkt', download_dir=os.path.join(BASE_DIR,'data/punkt'))
nltk.download('wordnet', download_dir=os.path.join(BASE_DIR,'data/wordnet'))

from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()


THRESHOLD = 0.25


model = load_model(os.path.join(BASE_DIR,'AI/resources/models/chatbot_model.h5'))
intents = json.loads(open(os.path.join(BASE_DIR,'AI/resources/data/intents.json')).read())
words = pickle.load(open(os.path.join(BASE_DIR,'AI/resources/pickles/words.pkl'), 'rb'))
classes = pickle.load(open(os.path.join(BASE_DIR,'AI/resources/pickles/classes.pkl'), 'rb'))

print('RESOURCES LOADED SUCESSFULLY!')

# applying lemmmatization

def add_data(data):
    new_data = intents
    for intent in data['intents']:
        temp = {}
        temp['tag'] = intent['tag']
        temp['patterns'] = intent['patterns']
        temp['responses'] = intent['responses']
        kt = True
        for tg in new_data['intents']:
            if tg['tag'] == temp['tag']:
                kt = False
                tg['patterns'].extend(intent['patterns'])
                tg['responses'].extend(intent['responses'])
        if kt:
            new_data['intents'].append(temp)
    jsonfile = open(os.path.join(BASE_DIR,'AI/resources/data/intents.json'),'w')
    jsonfile.write(json.dumps(new_data, indent=4))
    jsonfile.close 


def build_model():
    words = []
    classes = []
    documents = []
    ignore_words = ["?", "!"]
    data_file = open(os.path.join(BASE_DIR,'AI/resources/data/intents.json')).read()
    intents = json.loads(data_file)
    for intent in intents['intents']:
        for pattern in intent['patterns']:
            w = nltk.word_tokenize(pattern)
            words.extend(w)
            documents.append((w, intent['tag']))
            if intent['tag'] not in classes:
                classes.append(intent['tag'])
                
    # lemmatize
    words = [lemmatizer.lemmatize(w.lower())
        for w in words if w not in ignore_words]
    words = sorted(list(set(words)))
    classes = sorted(list(set(classes)))

    # print(len(documents), "documents")
    # print(len(classes), 'classes', classes)
    # print(len(words), "unique lemmatized words", words)

    pickle.dump(words, open(os.path.join(BASE_DIR,'AI/resources/pickles/words.pkl'), 'wb'))
    pickle.dump(classes, open(os.path.join(BASE_DIR,'AI/resources/pickles/classes.pkl'), 'wb'))
    pickle.dump(documents, open(os.path.join(BASE_DIR,'AI/resources/pickles/documents.pkl'), 'wb'))

    # Collecting the Training Data (Data Preprocessing)
    training = []
    output_empty = [0] * len(classes)
    for doc in documents:
        bag = []
        # gives only the lemmatized words from the documents.
        pattern_words = doc[0]
        # lemmatize the pattern_words
        pattern_words = [lemmatizer.lemmatize(
            word.lower()) for word in pattern_words]
        for w in words:
            bag.append(1) if w in pattern_words else bag.append(0)
        output_row = list(output_empty)
        output_row[classes.index(doc[1])] = 1
        training.append([bag, output_row])
    random.shuffle(training)
    training = np.array(training, dtype=object)
    train_x = list(training[:, 0])
    train_y = list(training[:, 1])
    print('Training data done')

    # Create Model
    model = Sequential()
    model.add(Dense(128, input_shape=(len(train_x[0]), ), activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(64, activation='relu'))
    model.add(Dropout(0.3))
    model.add(Dense(len(train_y[0]), activation='softmax'))
    adam = Adam(learning_rate=0.01, decay=1e-6)
    model.compile(loss='categorical_crossentropy',
        optimizer=adam, metrics=['accuracy'])
    hist = model.fit(np.array(train_x), np.array(train_y),
            epochs=200, verbose=0)
    model.save(os.path.join(BASE_DIR,'AI/resources/models/chatbot_model.h5'), hist)

    print("model created")

def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(
        word.lower()) for word in sentence_words]
    return sentence_words

# creating bag_of_words


def bag_of_words(sentence, words, show_details=True):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                bag[i] = 1
                if show_details:
                    print(f"found in bag: {w}")
    return (np.array(bag))


def predict_class(sentence, model):
    p = bag_of_words(sentence, words, show_details=False)
    res = model.predict(np.array([p]))[0]
    results = [[i, r] for i, r in enumerate(res) if r > THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append(
            {
                "intent": classes[r[0]],
                "probability": str(r[1])
            }
        )
    return return_list


def get_responses(ints, intents_json):
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']

    for i in list_of_intents:
        if i['tag'] == tag:
            result = random.choice(i['responses'])
            break
    return result


def chatbot_response(message):
    ints = predict_class(message, model)
    res = get_responses(ints, intents)
    return res


def main():
    while True:
        inp = input('You:\t')
        if inp == 'exit':
            break
        else:
            chatbot_result = chatbot_response(inp)
            print(f'bot:\t{chatbot_result}')


if __name__ == '__main__':
    print('TYPE exit TO QUIT!')
    main()
