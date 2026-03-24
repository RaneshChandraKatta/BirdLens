from keras import models

model = models.load_model('static/model/bird_species.h5')
print(model.summary())
