from selenium.webdriver.common.by import By
import time

class Navegador:
    def __init__(self, driver):
        self.driver = driver
    
    def click_numero_pagina(self, numero):
        try:
            time.sleep(2)
            paginas = self.driver.find_elements(By.CLASS_NAME, "ui-paginator-page")
            for pagina in paginas:
                if pagina.text == str(numero):
                    if "ui-state-active" not in pagina.get_attribute("class"):
                        pagina.click()
                        time.sleep(4)
                        return True
            return False
        except Exception as e:
            print(f"Error click_numero_pagina: {e}")
            return False
    
    def ir_siguiente_pagina(self):
        try:
            boton = self.driver.find_element(By.CLASS_NAME, "ui-paginator-next")
            if "ui-state-disabled" in boton.get_attribute("class"):
                return False
            boton.click()
            time.sleep(4)
            return True
        except Exception as e:
            print(f"Error ir_siguiente_pagina: {e}")
            return False