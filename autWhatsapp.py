from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

def send_whatsapp_message(phone_number, message):
    # Caminho para o chromedriver (precisa estar instalado)
    driver = webdriver.Chrome(executable_path='/caminho/para/seu/chromedriver')

    # Acessa o WhatsApp Web
    driver.get("https://web.whatsapp.com/")
    
    input("Pressione ENTER após escanear o QR Code")

    # Espera a página carregar
    time.sleep(10)

    # Monta a URL de chat com o número desejado
    url = f"https://web.whatsapp.com/send?phone={phone_number}&text={message}"
    driver.get(url)

    # Espera a página carregar o chat
    time.sleep(5)

    # Envia a mensagem
    input_box = driver.find_element_by_xpath('//div[@contenteditable="true"]')
    input_box.send_keys(Keys.ENTER)

    print(f"Mensagem enviada para {phone_number}")
    
    # Fecha o navegador após envio
    time.sleep(5)
    driver.quit()
