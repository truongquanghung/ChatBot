import random
import json
from tensorflow.keras.models import load_model
# from keras.models import load_model 
import numpy as np
import pickle
import nltk
nltk.download('punkt')
nltk.download('wordnet')


from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()


THRESHOLD = 0.25


model = load_model('/code/resources/models/chatbot_model.h5')
intents = json.loads(open('/code/resources/data/intents.json').read())
words = pickle.load(open('/code/resources/pickles/words.pkl', 'rb'))
classes = pickle.load(open('/code/resources/pickles/classes.pkl', 'rb'))

print('RESOURCES LOADED SUCESSFULLY!')

# applying lemmmatization


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
