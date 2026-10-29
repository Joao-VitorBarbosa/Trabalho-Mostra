import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# 1. Carregar modelo e dados
modelo = load_model('modelo_sinais.h5')
CLASSES = ["fist", "five", "none", "okay", "peace", "rad", "straight", "thumbs"]

test_datagen = ImageDataGenerator(rescale=1./255)
test_generator = test_datagen.flow_from_directory(
    'data/test', target_size=(100, 100), batch_size=32, 
    class_mode='categorical', shuffle=False)

# 2. Gerar Matriz de Confusão
predicoes = modelo.predict(test_generator)
classes_preditas = np.argmax(predicoes, axis=1)
classes_reais = test_generator.classes

matriz = confusion_matrix(classes_reais, classes_preditas)

plt.figure(figsize=(10, 8))
sns.heatmap(matriz, annot=True, fmt='d', cmap='Blues', xticklabels=CLASSES, yticklabels=CLASSES)
plt.title('Matriz de Confusão')
plt.ylabel('Classe Real')
plt.xlabel('Classe Predita')
plt.savefig('matriz_confusao.png')
print("Matriz de confusão salva como 'matriz_confusao.png'")