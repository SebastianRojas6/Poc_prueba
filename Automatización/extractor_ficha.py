from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import os

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
    
    def descargar_pdf(self, nomenclatura):
        try:
            print("      Buscando PDF...")
            time.sleep(2)
            
            tabla = self.driver.find_element(By.ID, "tbFicha:dtDocumentos_data")
            filas = tabla.find_elements(By.TAG_NAME, "tr")
            
            for fila in filas:
                try:
                    enlaces = fila.find_elements(By.TAG_NAME, "a")
                    for enlace in enlaces:
                        onclick = enlace.get_attribute("onclick")
                        if onclick and "descargaDocGeneral" in onclick:
                            match = re.search(r"descargaDocGeneral\('([^']+)','([^']+)','([^']+)'\)", onclick)
                            if match:
                                doc_id = match.group(1)
                                sistema = match.group(2)
                                nombre_archivo = match.group(3)
                                
                                print(f"      Descargando: {nombre_archivo}")
                                
                                url_descarga = f"https://prod2.seace.gob.pe/seacebus-uiwd-pub/downloadCustom/obtenerDocumento.xhtml?id={doc_id}&nombreArchivo={nombre_archivo}"
                                
                                self.driver.execute_script(f"window.open('{url_descarga}', '_blank');")
                                time.sleep(3)
                                
                                ventanas = self.driver.window_handles
                                if len(ventanas) > 1:
                                    self.driver.switch_to.window(ventanas[-1])
                                    time.sleep(2)
                                    self.driver.close()
                                    self.driver.switch_to.window(ventanas[0])
                                
                                pdf_dir = "pdfs_descargados"
                                if not os.path.exists(pdf_dir):
                                    os.makedirs(pdf_dir)
                                
                                ruta_local = os.path.join(pdf_dir, f"{nomenclatura}.pdf")
                                
                                print(f"      ✓ PDF descargado")
                                return ruta_local
                except Exception as e:
                    print(f"      Error en fila PDF: {e}")
                    continue
            
            print("      ⚠ No se encontró PDF")
            return ""
        except Exception as e:
            print(f"      Error al descargar PDF: {e}")
            return ""
    
    def extraer_todo(self, nomenclatura):
        info_conv = self.extraer_info_convocatoria()
        info_ent = self.extraer_info_entidad()
        info_proc = self.extraer_info_procedimiento()
        cronograma = self.extraer_cronograma()
        pdf_path = self.descargar_pdf(nomenclatura)
        
        return {
            **info_conv,
            **info_ent,
            **info_proc,
            'Cronograma': cronograma,
            'PDF_Path': pdf_path
        }