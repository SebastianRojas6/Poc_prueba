from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class ExtractorFicha:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 30)
    
    def extraer_info_convocatoria(self):
        try:
            data = {}
            tabla = self.driver.find_element(By.ID, "tbFicha:j_idt30")
            filas = tabla.find_elements(By.TAG_NAME, "tr")
            for fila in filas:
                celdas = fila.find_elements(By.TAG_NAME, "td")
                if len(celdas) >= 2:
                    clave = celdas[0].text.strip().replace(":", "")
                    valor = celdas[1].text.strip()
                    data[clave] = valor
            return data
        except:
            return {}
    
    def extraer_info_entidad(self):
        try:
            data = {}
            tabla = self.driver.find_element(By.ID, "tbFicha:j_idt73")
            filas = tabla.find_elements(By.TAG_NAME, "tr")
            for fila in filas:
                celdas = fila.find_elements(By.TAG_NAME, "td")
                if len(celdas) >= 2:
                    clave = celdas[0].text.strip().replace(":", "")
                    valor = celdas[1].text.strip()
                    data[clave] = valor
            return data
        except:
            return {}
    
    def extraer_info_procedimiento(self):
        try:
            data = {}
            tabla = self.driver.find_element(By.ID, "tbFicha:j_idt97")
            filas = tabla.find_elements(By.TAG_NAME, "tr")
            for fila in filas:
                celdas = fila.find_elements(By.TAG_NAME, "td")
                if len(celdas) >= 2:
                    clave = celdas[0].text.strip().replace(":", "")
                    valor = celdas[1].text.strip()
                    data[clave] = valor
            return data
        except:
            return {}
    
    def extraer_cronograma(self):
        try:
            cronograma = []
            tabla = self.driver.find_element(By.ID, "tbFicha:dtCronograma_data")
            filas = tabla.find_elements(By.TAG_NAME, "tr")
            for fila in filas:
                celdas = fila.find_elements(By.TAG_NAME, "td")
                if len(celdas) >= 3:
                    etapa_text = celdas[0].text.strip()
                    etapa = etapa_text.split('\n')[0] if '\n' in etapa_text else etapa_text
                    cronograma.append({
                        'Etapa': etapa,
                        'Fecha Inicio': celdas[1].text.strip(),
                        'Fecha Fin': celdas[2].text.strip()
                    })
            return cronograma
        except:
            return []
    
    def extraer_todo(self):
        info_conv = self.extraer_info_convocatoria()
        info_ent = self.extraer_info_entidad()
        info_proc = self.extraer_info_procedimiento()
        cronograma = self.extraer_cronograma()
        
        return {
            **info_conv,
            **info_ent,
            **info_proc,
            'Cronograma': cronograma
        }