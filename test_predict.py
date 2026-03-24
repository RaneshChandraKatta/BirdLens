import numpy as np
import tensorflow as tf
from keras import models

model = models.load_model('static/model/bird_species.h5')

def predict(img_arr):
    img_arr = img_arr.astype(np.float32)
    img_arr = np.expand_dims(img_arr, axis=0)
    result = model.predict(img_arr)
    return result

# Zeros
zeros = predict(np.zeros((224, 224, 3)))
print("Zeros probabilities:", zeros)

# 255s
max_vals = predict(np.ones((224, 224, 3)) * 255)
print("255s probabilities:", max_vals)

# Adjusted (normalized) 255s
norm_vals = predict(np.ones((224, 224, 3)))
print("Normalized 1s probabilities:", norm_vals)

# Normal image (random)
rand_vals = predict(np.random.randint(0, 256, (224, 224, 3)))
print("Random 0-255 probabilities:", rand_vals)

rand_norm = predict(np.random.rand(224, 224, 3))
print("Random 0-1 probabilities:", rand_norm)
