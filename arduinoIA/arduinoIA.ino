#include <Servo.h>

int echo = 2; 
int trig = 3; 
double tempo, cm; 
int buzzer = 4; 

Servo servoMotor; 

int alarmeAtivo = 0; 
int pessoaSaiu = 0; 

int senhaCorreta[] = {0, 1, 4}; 
int tamanhoSenhaCorreta = 3; 

int senhaDigitada[9]; 
int cliques = 0; 

void setup()
{
  pinMode(trig, OUTPUT); 
  pinMode(echo, INPUT); 
  pinMode(buzzer, OUTPUT); 
  
  Serial.begin(9600); 
  
  servoMotor.attach(5); 
  servoMotor.write(0); // Garante que inicie trancado
}

void loop()
{
  // --- Lógica do Sensor Ultrassônico ---
  digitalWrite(trig, LOW); 
  delayMicroseconds(2); 
  digitalWrite(trig, HIGH); 
  delayMicroseconds(10); 
  digitalWrite(trig, LOW); 
  tempo = pulseIn(echo, HIGH, 25000); 
  cm = tempo/58; 

  // --- DEBUG DO SENSOR (Apague ou comente na hora de usar o Python) ---
  Serial.print("Distancia lida: ");
  Serial.print(cm);
  Serial.println(" cm");
  // ------------------------------------------------------------

  // DISTÂNCIA AJUSTADA PARA A MAQUETE (10 centímetros)
  int distanciaGatilho = 10; 

  // Se o objeto chegar a MENOS de 10cm, o alarme dispara
  if(cm > 0 && cm < distanciaGatilho && pessoaSaiu == 1) {
     alarmeAtivo = 1; 
     pessoaSaiu = 0; 
  }

  // Se não tiver ninguém a menos de 10cm, o sistema "arma" esperando
  if(cm >= distanciaGatilho || cm <= 0){
    pessoaSaiu = 1; 
  }

  // --- CORREÇÃO DA LÓGICA DO ALARME ---
  if (alarmeAtivo == 1) { 
    // APENAS o alarme toca! A porta se mantém fechada.
    tone(buzzer, 500); 
  } else {
    noTone(buzzer); 
  }

  // --- Lógica de Leitura da IA ---
  if (Serial.available() > 0) { 
    char sinalRecebido = Serial.read(); 

    if (sinalRecebido >= '0' && sinalRecebido <= '7') { 
      
      int gestoID = sinalRecebido - '0'; 
      
      if (gestoID == 2) { 
         cliques = 0; 
         noTone(buzzer); 
         tone(buzzer, 1500); delay(100); noTone(buzzer); 
      }
      else {
        registrarSinal(gestoID); 
      }
    }
  }

  delay(50); 
}

void registrarSinal(int gestoID) { 
  if (cliques < tamanhoSenhaCorreta) { 
    senhaDigitada[cliques] = gestoID; 
    cliques++; 
    
    noTone(buzzer); 
    tone(buzzer, 1000); 
    delay(150); 
    noTone(buzzer); 

    if (cliques == tamanhoSenhaCorreta) { 
        verificarSenha(); 
    }
  }
}

void verificarSenha() { 
  bool acertou = true; 

  for (int i = 0; i < tamanhoSenhaCorreta; i++) { 
    if (senhaDigitada[i] != senhaCorreta[i]) { 
      acertou = false; 
      break; 
    }
  }

  if (acertou) { 
    alarmeAtivo = 0; 
    noTone(buzzer); 
    
    tone(buzzer, 2000); delay(200); noTone(buzzer); delay(100); 
    tone(buzzer, 2000); delay(200); noTone(buzzer); 
    
    // --- LÓGICA DA PORTA ---
    servoMotor.write(90); // Abre a porta (já que a senha está correta)
    delay(5000);          // Mantém aberta por 5 segundos
    servoMotor.write(0);  // Tranca a porta novamente
    
  } else {
    noTone(buzzer); 
    tone(buzzer, 200); delay(500); noTone(buzzer); 
    
    delay(2500); 
  }
  
  while (Serial.available() > 0) { 
    Serial.read(); 
  }
  
  cliques = 0; 
}