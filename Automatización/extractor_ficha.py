from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import os
import glob

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
    
    def descargar_documento(self, nomenclatura):
        try:
            print("      Buscando documento...")
            time.sleep(2)
            
            chrome_options = self.driver.capabilities
            download_dir = os.path.abspath("documentos_descargados")
            if not os.path.exists(download_dir):
                os.makedirs(download_dir)
            
            archivos_antes = set(glob.glob(os.path.join(download_dir, "*")))
            
            tabla = self.driver.find_element(By.ID, "tbFicha:dtDocumentos_data")
            filas = tabla.find_elements(By.TAG_NAME, "tr")
            
            for fila in filas:
                try:
                    celdas = fila.find_elements(By.TAG_NAME, "td")
                    if len(celdas) >= 4:
                        tipo_doc = celdas[2].text.strip()
                        
                        if "Bases" in tipo_doc:
                            enlaces = celdas[3].find_elements(By.TAG_NAME, "a")
                            
                            for enlace in enlaces:
                                onclick = enlace.get_attribute("onclick")
                                if onclick and "descargaDocGeneral" in onclick:
                                    match = re.search(r"descargaDocGeneral\('([^']+)','([^']+)','([^']+)'\)", onclick)
                                    if match:
                                        nombre_archivo = match.group(3)
                                        print(f"      Encontrado: {nombre_archivo}")
                                        
                                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", enlace)
                                        time.sleep(1)
                                        
                                        try:
                                            self.driver.execute_script("arguments[0].click();", enlace)
                                        except:
                                            enlace.click()
                                        
                                        print(f"      Esperando descarga...")
                                        time.sleep(5)
                                        
                                        archivos_despues = set(glob.glob(os.path.join(download_dir, "*")))
                                        nuevos_archivos = archivos_despues - archivos_antes
                                        
                                        if nuevos_archivos:
                                            archivo_descargado = list(nuevos_archivos)[0]
                                            extension = os.path.splitext(archivo_descargado)[1]
                                            nombre_limpio = nomenclatura.replace("/", "-").replace("\\", "-")
                                            ruta_final = os.path.join(download_dir, f"{nombre_limpio}{extension}")
                                            
                                            if os.path.exists(archivo_descargado):
                                                if os.path.exists(ruta_final):
                                                    os.remove(ruta_final)
                                                os.rename(archivo_descargado, ruta_final)
                                                print(f"      ✓ Documento descargado: {ruta_final}")
                                                return ruta_final
                                        else:
                                            print(f"      ⚠ No se detectó descarga")
                                            return ""
                except Exception as e:
                    print(f"      Error en fila: {e}")
                    continue
            
            print("      ⚠ No se encontró documento de Bases")
            return ""
        except Exception as e:
            print(f"      Error al descargar documento: {e}")
            return ""
    
    def extraer_todo(self, nomenclatura):
        info_conv = self.extraer_info_convocatoria()
        info_ent = self.extraer_info_entidad()
        info_proc = self.extraer_info_procedimiento()
        cronograma = self.extraer_cronograma()
        doc_path = self.descargar_documento(nomenclatura)
        
        return {
            **info_conv,
            **info_ent,
            **info_proc,
            'Cronograma': cronograma,
            'Documento_Path': doc_path
        }