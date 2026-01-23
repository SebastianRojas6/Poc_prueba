from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
import time
from datetime import datetime
import os

class SEACEScraper:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 30)
        self.url = "https://prod2.seace.gob.pe/seacebus-uiwd-pub/buscadorPublico/buscadorPublico.xhtml"
        self.datos_totales = []
        
    def abrir_pagina(self):
        print("Abriendo página de SEACE...")
        self.driver.get(self.url)
        time.sleep(4)
        
    def click_tab_procedimientos(self):
        print("Navegando a pestaña de Procedimientos de Selección...")
        try:
            tab = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//a[contains(@href, '#tbBuscador:tab1')]")
            ))
            tab.click()
            time.sleep(3)
            print("✓ Pestaña de Procedimientos de Selección activa")
        except Exception as e:
            print(f"Error al hacer clic en la pestaña: {e}")
            raise
    
    def seleccionar_anio_primefaces(self, anio):
        print(f"Seleccionando año {anio}...")
        try:
            time.sleep(2)
            select_id = "tbBuscador:idFormBuscarProceso:anioConvocatoria_input"
            select_element = self.wait.until(
                EC.presence_of_element_located((By.ID, select_id))
            )
            select = Select(select_element)
            select.select_by_value(str(anio))
            time.sleep(1)
            print(f"✓ Año {anio} seleccionado")
        except Exception as e:
            print(f"Error al seleccionar año {anio}: {e}")
            try:
                print("Intentando método alternativo con JavaScript...")
                script = f"""
                var select = document.getElementById('tbBuscador:idFormBuscarProceso:anioConvocatoria_input');
                select.value = '{anio}';
                select.dispatchEvent(new Event('change'));
                """
                self.driver.execute_script(script)
                time.sleep(1)
                print(f"✓ Año {anio} seleccionado (método alternativo)")
            except Exception as e2:
                print(f"Error en método alternativo: {e2}")
                raise
    
    def click_buscar(self):
        print("Ejecutando búsqueda...")
        try:
            boton_buscar = self.wait.until(EC.element_to_be_clickable(
                (By.ID, "tbBuscador:idFormBuscarProceso:btnBuscarSelToken")
            ))
            boton_buscar.click()
            time.sleep(4)
            print("✓ Búsqueda ejecutada")
        except Exception as e:
            print(f"Error al hacer clic en Buscar: {e}")
            raise
    
    def esperar_resultados(self):
        print("Esperando resultados...")
        try:
            self.wait.until(EC.presence_of_element_located(
                (By.ID, "tbBuscador:idFormBuscarProceso:dtProcesos_data")
            ))
            time.sleep(2)
            print("✓ Resultados cargados")
            return True
        except TimeoutException:
            print("⚠ No se encontraron resultados o timeout")
            return False
    
    def verificar_sin_resultados(self):
        try:
            tabla = self.driver.find_element(By.ID, 
                "tbBuscador:idFormBuscarProceso:dtProcesos_data")
            if "No se encontraron Datos" in tabla.text:
                print("⚠ No hay datos para este año")
                return True
        except:
            pass
        return False
    
    def extraer_datos_pagina(self):
        try:
            tabla = self.driver.find_element(By.ID, 
                "tbBuscador:idFormBuscarProceso:dtProcesos_data")
            filas = tabla.find_elements(By.TAG_NAME, "tr")
            datos_pagina = []
            for fila in filas:
                try:
                    celdas = fila.find_elements(By.TAG_NAME, "td")
                    if len(celdas) >= 13:
                        dato = {
                            'N°': celdas[0].text.strip(),
                            'Nombre o Sigla de la Entidad': celdas[1].text.strip(),
                            'Fecha y Hora de Publicacion': celdas[2].text.strip(),
                            'Nomenclatura': celdas[3].text.strip(),
                            'Reiniciado Desde': celdas[4].text.strip(),
                            'Objeto de Contratación': celdas[5].text.strip(),
                            'Descripción de Objeto': celdas[6].text.strip(),
                            'Código SNIP': celdas[7].text.strip(),
                            'Código Unico de Inversion': celdas[8].text.strip(),
                            'VR / VE / Cuantía de la contratación': celdas[9].text.strip(),
                            'Moneda': celdas[10].text.strip(),
                            'Versión SEACE': celdas[11].text.strip()
                        }
                        if dato['N°'] and dato['Nombre o Sigla de la Entidad']:
                            datos_pagina.append(dato)
                except Exception as e:
                    continue
            return datos_pagina
        except Exception as e:
            print(f"Error al extraer datos: {e}")
            return []
    
    def obtener_info_paginacion(self):
        try:
            paginador = self.driver.find_element(By.ID, 
                "tbBuscador:idFormBuscarProceso:dtProcesos_paginator_bottom")
            span_current = paginador.find_element(By.CLASS_NAME, "ui-paginator-current")
            texto = span_current.text
            if "Página:" in texto:
                partes = texto.split("Página:")[1].strip().rstrip("]").strip()
                pagina_actual, total_paginas = partes.split("/")
                return int(pagina_actual), int(total_paginas)
        except Exception as e:
            print(f"No se pudo obtener info de paginación: {e}")
            return 1, 1
        return 1, 1
    
    def click_numero_pagina(self, numero_pagina):
        try:
            paginas = self.driver.find_elements(By.CLASS_NAME, "ui-paginator-page")
            for pagina in paginas:
                if pagina.text == str(numero_pagina):
                    if "ui-state-active" not in pagina.get_attribute("class"):
                        pagina.click()
                        time.sleep(3)
                        return True
            return False
        except Exception as e:
            print(f"Error al hacer clic en página {numero_pagina}: {e}")
            return False
    
    def ir_siguiente_pagina(self):
        try:
            boton_siguiente = self.driver.find_element(By.CLASS_NAME, "ui-paginator-next")
            if "ui-state-disabled" in boton_siguiente.get_attribute("class"):
                return False
            boton_siguiente.click()
            time.sleep(3)
            return True
        except:
            return False
    
    def scrape_anio(self, anio):
        print(f"\n{'='*60}")
        print(f"PROCESANDO AÑO {anio}")
        print(f"{'='*60}")
        
        self.seleccionar_anio_primefaces(anio)
        self.click_buscar()
        
        if not self.esperar_resultados():
            return
        
        if self.verificar_sin_resultados():
            return
        
        pagina_actual, total_paginas = self.obtener_info_paginacion()
        print(f"Total de páginas detectadas: {total_paginas}")
        
        for num_pagina in range(1, total_paginas + 1):
            print(f"\n{'─'*40}")
            print(f"Procesando página {num_pagina}/{total_paginas}")
            print(f"{'─'*40}")
            
            datos_pagina = self.extraer_datos_pagina()
            if datos_pagina:
                self.datos_totales.extend(datos_pagina)
                print(f"✓ {len(datos_pagina)} registros extraídos")
            else:
                print("⚠ No se extrajeron datos de esta página")
            
            if num_pagina < total_paginas:
                print(f"Navegando a página {num_pagina + 1}...")
                if not self.click_numero_pagina(num_pagina + 1):
                    if not self.ir_siguiente_pagina():
                        print("⚠ No se pudo navegar a la siguiente página")
                        break
        
        registros_anio = len([d for d in self.datos_totales 
                             if str(anio) in d.get('Fecha y Hora de Publicacion', '')])
        print(f"\n✓ Año {anio} completado: {registros_anio} registros")
    
    def exportar_excel(self, nombre_archivo=None):
        if not self.datos_totales:
            print("\n⚠ No hay datos para exportar")
            return
        
        if nombre_archivo is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"SEACE_Procedimientos_{timestamp}.xlsx"
        
        df = pd.DataFrame(self.datos_totales)
        output_dir = "resultados_seace"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        ruta_completa = os.path.join(output_dir, nombre_archivo)
        
        with pd.ExcelWriter(ruta_completa, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Procedimientos', index=False)
            worksheet = writer.sheets['Procedimientos']
            for i, col in enumerate(df.columns):
                max_length = max(df[col].astype(str).map(len).max(), len(col)) + 2
                col_letter = chr(65 + i) if i < 26 else chr(65 + i//26 - 1) + chr(65 + i%26)
                worksheet.column_dimensions[col_letter].width = min(max_length, 50)
        
        print(f"\n{'='*60}")
        print(f"✓ DATOS EXPORTADOS EXITOSAMENTE")
        print(f"{'='*60}")
        print(f"Archivo: {ruta_completa}")
        print(f"Total de registros: {len(self.datos_totales)}")
        print(f"\nResumen por año:")
        for anio in [2024, 2025, 2026]:
            count = len([d for d in self.datos_totales 
                        if f"/{anio}" in d.get('Fecha y Hora de Publicacion', '')])
            if count > 0:
                print(f"  - {anio}: {count} registros")
        print(f"{'='*60}\n")
    
    def ejecutar(self, anios=[2024, 2025, 2026]):
        try:
            self.abrir_pagina()
            self.click_tab_procedimientos()
            for anio in anios:
                self.scrape_anio(anio)
            self.exportar_excel()
        except Exception as e:
            print(f"\n❌ ERROR CRÍTICO: {e}")
            import traceback
            traceback.print_exc()
        finally:
            print("\nCerrando navegador en 5 segundos...")
            time.sleep(5)
            self.driver.quit()

def main():
    scraper = SEACEScraper()
    scraper.ejecutar()
    print("\n✓ Proceso completado. Presiona Enter para salir...")
    input()

if __name__ == "__main__":
    main()