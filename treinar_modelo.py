import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import matplotlib.pyplot as plt

LARGURA_IMG, ALTURA_IMG = 100, 100
TAMANHO_LOTE = 32
EPOCAS = 30

# Validação e Teste (Com espelhamento para aprender a mão esquerda)
gerador_dados_treino = ImageDataGenerator(
    rescale=1./255,
    horizontal_flip=True 
)

# Validação e Teste (Sem espelhamento, analisa os dados originais)
gerador_dados_teste = ImageDataGenerator(rescale=1./255)

gerador_treino = gerador_dados_treino.flow_from_directory(
    'data/train',
    target_size=(LARGURA_IMG, ALTURA_IMG),
    batch_size=TAMANHO_LOTE,
    class_mode='categorical'
)

gerador_validacao = gerador_dados_teste.flow_from_directory(
    'data/validation',
    target_size=(LARGURA_IMG, ALTURA_IMG),
    batch_size=TAMANHO_LOTE,
    class_mode='categorical'
)

modelo = Sequential([

    Conv2D(32, (3, 3), activation='relu', input_shape=(LARGURA_IMG, ALTURA_IMG, 3)),
    MaxPooling2D(pool_size=(2, 2)),
    
    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D(pool_size=(2, 2)),
    
    Conv2D(128, (3, 3), activation='relu'),
    MaxPooling2D(pool_size=(2, 2)),
    
    # Tomada de decisão
    Flatten(),
    Dense(128, activation='relu'),
    Dropout(0.5), 
    Dense(8, activation='softmax') 
])

modelo.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

print("\nIniciando o treinamento. A IA vai começar a estudar as silhuetas...")

# Guardamos o progresso na variável 'historico_treinamento' para gerar os gráficos depois
historico_treinamento = modelo.fit(gerador_treino, epochs=EPOCAS, validation_data=gerador_validacao)

print("\n--------------------------------------------------")
print("Avaliando o modelo com a pasta 'test' (dados nunca vistos)...")

gerador_teste = gerador_dados_teste.flow_from_directory(
    'data/test',
    target_size=(LARGURA_IMG, ALTURA_IMG),
    batch_size=TAMANHO_LOTE,
    class_mode='categorical',
    shuffle=False 
)

perda, acuracia = modelo.evaluate(gerador_teste)

print("\nRESULTADOS FINAIS PARA O RELATÓRIO:")
print(f"-> Acurácia real no conjunto de teste: {acuracia * 100:.2f}%")
print(f"-> Perda (Loss) no conjunto de teste: {perda:.4f}")
print("--------------------------------------------------\n")

modelo.save('modelo_sinais.h5')

plt.figure(figsize=(12, 4))

# Gráfico de Acurácia (O quanto a IA acertou)
plt.subplot(1, 2, 1)
plt.plot(historico_treinamento.history['accuracy'], label='Treino')
plt.plot(historico_treinamento.history['val_accuracy'], label='Validação')
plt.title('Acurácia do Modelo')
plt.xlabel('Época')
plt.ylabel('Acurácia')
plt.legend()

# Gráfico de Custo/Perda (O quanto a IA errou)
plt.subplot(1, 2, 2)
plt.plot(historico_treinamento.history['loss'], label='Treino')
plt.plot(historico_treinamento.history['val_loss'], label='Validação')
plt.title('Custo (Loss) do Modelo')
plt.xlabel('Época')
plt.ylabel('Custo (Perda)')
plt.legend()

plt.tight_layout()
plt.savefig('grafico_treinamento.png')
print("Gráfico de treinamento salvo como 'grafico_treinamento.png'")
print("Treinamento concluído! O arquivo 'modelo_sinais.h5' está pronto para ser usado com o Arduino.")