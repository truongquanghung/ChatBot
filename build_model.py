from tensorflow.keras.optimizers import SGD 
from tensorflow.keras.layers import Dense, Activation, Dropout 
from tensorflow.keras.models import Sequential
from tensorflow.keras.models import load_model
import random
import json
import numpy as np
import pickle
import nltk

nltk.download('punkt')
nltk.download('wordnet')

from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()

words = []
classes = []
documents = []
ignore_words = ["?", "!"]
data_file = open('resources\data\intents.json').read()
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

print(len(documents), "documents")
print(len(classes), 'classes', classes)
print(len(words), "unique lemmatized words", words)

pickle.dump(words, open('resources\pickles\words.pkl', 'wb'))
pickle.dump(classes, open('resources\pickles\classes.pkl', 'wb'))
pickle.dump(documents, open('resources\pickles\documents.pkl', 'wb'))

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
training = np.array(training)
train_x = list(training[:, 0])
train_y = list(training[:, 1])
print('Training data done')

# Create Model
model = Sequential()
model.add(Dense(128, input_shape=(len(train_x[0]), ), activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(len(train_y[0]), activation='softmax'))
sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
model.compile(loss='categorical_crossentropy',
      optimizer=sgd, metrics=['accuracy'])
hist = model.fit(np.array(train_x), np.array(train_y),
         epochs=200, batch_size=5, verbose=1)
model.save('resources\models\chatbot_model.h5', hist)

print("model created")