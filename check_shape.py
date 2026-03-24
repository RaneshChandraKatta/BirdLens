from keras import models

model = models.load_model('static/model/bird_species.h5')
print("Model Inputs:", model.inputs)
print("Input Shape:", model.input_shape)
for layer in model.layers:
    print(layer.name, layer.input_shape, layer.output_shape)
