import cv2
import numpy as np
import serial
import time
from tensorflow.keras.models import load_model

try:
    arduino = serial.Serial('COM6', 9600, timeout=1) 
    time.sleep(2)
    print("Conectado ao Arduino!")
except:
    print("AVISO: Arduino não encontrado. Testando apenas a IA na câmera.")
    arduino = None

modelo = load_model('modelo_sinais.h5')
IMG_WIDTH, IMG_HEIGHT = 100, 100

CLASSES = ["punho", "cinco", "nenhum", "ok", "paz", "irado", "reto", "joia"]

cap = cv2.VideoCapture(0)
print("Câmera ligada. Faça os sinais na tela!")

# Variáveis para controle de tempo e confirmação
gesto_atual = None
tempo_inicio_gesto = 0
tempo_necessario = 2.5 
ultimo_sinal_enviado = None 
tempo_ultimo_envio = 0

sinais_digitados = []
SENHA_CORRETA = [0, 1, 4] 
mensagem_resultado = ""
cor_resultado = (0, 0, 0)
tempo_resultado = 0

while True:
    ret, frame = cap.read()
    if not ret: break
        
    frame = cv2.flip(frame, 1)
    frame_display = frame.copy()
    
    # Pré-processamento da imagem
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_skin = np.array([0, 20, 70], dtype=np.uint8)
    upper_skin = np.array([20, 255, 255], dtype=np.uint8)
    mask = cv2.inRange(hsv, lower_skin, upper_skin)
    
    mask = cv2.GaussianBlur(mask, (5, 5), 0)
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.erode(mask, kernel, iterations=1)
    mask = cv2.dilate(mask, kernel, iterations=1 )
    
    silhueta_completa = np.zeros(frame.shape, dtype=np.uint8)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    texto_tela = "Procurando mao..."
    cor_texto = (0, 0, 255)

    if contours:
        maior_contorno = max(contours, key=cv2.contourArea)
        if cv2.contourArea(maior_contorno) > 3000:

            # Cria um molde apenas com o contorno da mão preenchido
            molde_mao = np.zeros(mask.shape, dtype=np.uint8)
            cv2.drawContours(molde_mao, [maior_contorno], -1, 255, -1)
            silhueta_limpa = cv2.bitwise_and(mask, mask, mask=molde_mao)
            silhueta_completa = cv2.cvtColor(silhueta_limpa, cv2.COLOR_GRAY2BGR)
            
            x, y, w, h = cv2.boundingRect(maior_contorno)
            tamanho_max = max(w, h)
            centro_x, centro_y = x + w//2, y + h//2
            
            start_x = max(0, centro_x - tamanho_max//2)
            start_y = max(0, centro_y - tamanho_max//2)
            end_x = min(frame.shape[1], start_x + tamanho_max)
            end_y = min(frame.shape[0], start_y + tamanho_max)
            
            recorte_silhueta = silhueta_completa[start_y:end_y, start_x:end_x]
            
            if recorte_silhueta.size > 0:
                cv2.rectangle(frame_display, (start_x, start_y), (end_x, end_y), (255, 0, 0), 2)
                
                img_resized = cv2.resize(recorte_silhueta, (IMG_WIDTH, IMG_HEIGHT))
                img_array_normal = np.expand_dims(img_resized, axis=0) / 255.0
                
                img_flipped = cv2.flip(img_resized, 1)
                img_array_flipped = np.expand_dims(img_flipped, axis=0) / 255.0

                predicao_normal = modelo.predict(img_array_normal, verbose=0)[0]
                predicao_flipped = modelo.predict(img_array_flipped, verbose=0)[0]

                confianca_normal = np.max(predicao_normal)
                confianca_flipped = np.max(predicao_flipped)

                if confianca_normal >= confianca_flipped:
                    predicao = predicao_normal
                    confianca = confianca_normal
                else:
                    predicao = predicao_flipped
                    confianca = confianca_flipped

                digito = np.argmax(predicao)
                
                nome_sinal = CLASSES[digito]
                
                if confianca > 0.80:
                    if digito == gesto_atual:
                        tempo_decorrido = time.time() - tempo_inicio_gesto
                        
                        if tempo_decorrido < tempo_necessario:
                            texto_tela = f"Segure {nome_sinal}: {tempo_decorrido:.1f}s"
                            cor_texto = (0, 165, 255)
                        else:
                            texto_tela = f"ENVIADO: {nome_sinal}!"
                            cor_texto = (0, 255, 0)
                            
                            if (time.time() - tempo_ultimo_envio) > 2.0 or digito != ultimo_sinal_enviado:
                                if arduino:
                                    arduino.write(str(digito).encode()) 
                        
                                if digito == 2:
                                    sinais_digitados.clear()
                                    mensagem_resultado = "Resetado!"
                                    cor_resultado = (0, 165, 255)
                                    tempo_resultado = time.time()
                                else:
                                    if len(sinais_digitados) == 0:
                                        mensagem_resultado = ""
                                        
                                    sinais_digitados.append(digito)
                                    
                                    if len(sinais_digitados) == 3: 
                                        if sinais_digitados == SENHA_CORRETA:
                                            mensagem_resultado = "SENHA CORRETA!"
                                            cor_resultado = (0, 255, 0) 
                                        else:
                                            mensagem_resultado = "SENHA INCORRETA!"
                                            cor_resultado = (0, 0, 255) 
                                            
                                        tempo_resultado = time.time()
                                        sinais_digitados.clear() 
                                ultimo_sinal_enviado = digito
                                tempo_ultimo_envio = time.time()
                                print(f"-> Gesto Confirmado e Enviado: {nome_sinal} (ID: {digito})")
                    else:
                        gesto_atual = digito
                        tempo_inicio_gesto = time.time()
                        texto_tela = f"Detectado: {nome_sinal}"
                        cor_texto = (0, 255, 255)
                else:
                    gesto_atual = None
                    texto_tela = "Lendo..."
                    cor_texto = (0, 0, 255)
        else:
            gesto_atual = None

    # Exibe a interface com a mensagem de temporização principal
    cv2.putText(frame_display, texto_tela, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, cor_texto, 2)
    
    # Exibe o progresso da senha na cor Ciano
    texto_senha = f"Sinais lidos: {len(sinais_digitados)}/3"
    cv2.putText(frame_display, texto_senha, (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
    
    # Mostra a mensagem de correta/incorreta por 4 segundos
    if mensagem_resultado != "" and (time.time() - tempo_resultado) < 4.0:
        cv2.putText(frame_display, mensagem_resultado, (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.8, cor_resultado, 2)

    cv2.imshow('Leitor de Sinais (Original)', frame_display)
    cv2.imshow('O que a IA enxerga', silhueta_completa)

    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()
if arduino: arduino.close()