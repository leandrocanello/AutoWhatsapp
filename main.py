from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from fastapi.middleware.cors import CORSMiddleware
import os
import time

# Instância do FastAPI
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # Permite o frontend no localhost:8080
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos os headers
)

# Modelo para receber os dados via API
class MessageData(BaseModel):
    phone_numbers: List[str]  # Lista de números de telefone
    message: str              # Mensagem a ser enviada

# Inicializa o WebDriver para o WhatsApp Web
def init_driver():
    print("Inicializando o WebDriver...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.get("https://web.whatsapp.com/")
    print("Por favor, escaneie o QR Code no WhatsApp Web.")
    
    try:
        # Espera pelo carregamento da página e pelo campo de busca ou barra lateral
        WebDriverWait(driver, 300).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "canvas"))
        )
        print("QR code escaneado com sucesso! Aguardando o campo de mensagem.")
        
        # Minimiza a janela do Chrome usando o xdotool (somente para Linux)
        os.system("xdotool search --onlyvisible --class chrome windowminimize")
        print("WhatsApp Web conectado e janela minimizada!")
        return driver
    except Exception as e:
        print(f"Erro ao conectar com o WhatsApp Web: {str(e)}")
        driver.quit()
        return None

# Função para enviar mensagem para um número de telefone via WhatsApp Web
def send_whatsapp_message(driver, phone_number, message):
    # Gera a URL do WhatsApp Web para enviar a mensagem
    url = f"https://web.whatsapp.com/send?phone={phone_number}&text={message}"
    driver.get(url)
    
    try:
        print(f"Mensagem pronta para {phone_number}")
        send_button = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span[data-icon='send']"))
        )
        send_button.click()
        print(f"Mensagem enviada para {phone_number}")
    except Exception as e:
        print(f"Erro ao enviar mensagem para {phone_number}: {str(e)}")


# Rota para enviar mensagens via API
@app.post("/enviarMensagem")
def send_message(data: MessageData):
    # Inicializa o driver para cada requisição
    driver = init_driver()
    
    if driver is None:
        return {"status": "Falha ao conectar no WhatsApp Web."}

    # Para cada número de telefone na lista, enviar a mensagem
    for phone_number in data.phone_numbers:
        try:
            send_whatsapp_message(driver, phone_number, data.message)
            time.sleep(2)  # Pausa entre o envio das mensagens
        except Exception as e:
            print(f"Erro ao enviar mensagem para {phone_number}: {str(e)}")
    
    # Fechar o navegador após enviar todas as mensagens
    driver.quit()

    return {"status": "Mensagens enviadas com sucesso!"}

# Rodando o servidor FastAPI
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
