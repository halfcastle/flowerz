# -*- coding: utf-8 -*-
"""flowergen.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1fMpXVw_kXqchA_QwLku8jGY3HyDHJK_J
"""

import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np
import json
import pandas as pd

import tensorflow_hub as hub
from tensorflow.keras.layers.experimental import preprocessing
from tensorflow.keras import layers
import platform
import time
import pathlib
import os

flowers=pd.read_csv("https://raw.githubusercontent.com/halfcastle/flowerz/main/language-of-flowers.csv")

flowers.head()

flowers.drop(['Color'],axis=1)

cleaned = flowers["Flower"]
text = "\n".join(cleaned[0:])
text

len(text)

print(text[0:100])

def split(raw_text, max_len, step_size = 1):

    lines = []
    next_chars = []

    for i in range(0, len(text) - max_len, step_size):
        lines.append(text[i:i+max_len])
        next_chars.append(text[i+max_len])
    
    return lines, next_chars

max_len = 15

lines, next_chars =  split(text, max_len = max_len, step_size = 1)
for i in range(0, 5):
    print(lines[i] + "     =>    " + next_chars[i])

chars = sorted(set(text))
char_indices = {char : chars.index(char) for char in chars}
X = np.zeros((len(lines), max_len, len(chars)))
y = np.zeros((len(lines), 1), dtype = np.int32)
for i, line in enumerate(lines):
	for t, char in enumerate(line):
		X[i, t, char_indices[char]] = 1
	y[i] = char_indices[next_chars[i]]

train_len = int(0.7*X.shape[0])
X_train = X[0:train_len]
X_val = X[train_len:]

y_train = y[0:train_len]
y_val  = y[train_len:]

model = tf.keras.models.Sequential([
    layers.LSTM(128, name = "LSTM", input_shape=(max_len, len(chars))),
    layers.Dense(len(chars))        
])
model.compile(loss = tf.keras.losses.SparseCategoricalCrossentropy(from_logits = True), 
              optimizer = "adam")

model.fit(X_train, 
          y_train,
          validation_data= (X_val, y_val),
          batch_size=128, epochs = 50)

def sample(preds, temp):
    
    # format the model predictions
    preds = np.asarray(preds).astype("float64")
    
    # construct normalized Boltzman with temp
    probs = np.exp(preds/temp)
    probs = probs / probs.sum()
    
    # sample from Boltzman
    samp = np.random.multinomial(1, probs, 1)
    return np.argmax(samp)

def generate_string(seed_index, temp, gen_length, model): 
    
    # sequence of integer indices for generated text
    gen_seq = np.zeros((max_len + gen_length, len(chars)))
    
    # first part of the generated indices actually corresponds to the real text
    seed = X[seed_index]
    gen_seq[0:max_len] = seed
    
    # character version
    gen_text = lines[seed_index]
    
    # main loop. 
    # at each stage we are going to get a single 
    # character from the model prediction (with the sample function)
    # and then feed that character BACK into the model as "data"
    # for the next prediction
    for i in range(0, gen_length):
        
        # this corresponds to the part of the generated
        # text that the model can "see"
        window = gen_seq[i: i + max_len]
        
        # get the prediction and sample a single index
        preds = model.predict(np.array([window]))[0]
        next_index = sample(preds, temp)
        
        # add sampled index to the current output
        gen_seq[max_len + i, next_index] = True
        
        # create the string version
        next_char = chars[next_index]
        gen_text += next_char
    
    # only return the string version because that's what we care about
    return(gen_text)

gen_length = 10
seed_index = 2

for temp in [0.01, 0.02, 0.03, 0.04, 0.05]:

    gen = generate_string(seed_index, temp, gen_length, model)

    print(4*"-")
    print("TEMPERATURE: " + str(temp))
    print(gen[:-gen_length], end="")
    print(" => ", end = "")
    print(gen[-gen_length:], "")

gen_length = 5
seed_index = 7

gen = generate_string(seed_index, 0.02, gen_length, model)

import re
print(gen)