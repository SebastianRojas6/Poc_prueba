from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time
from config import URL, TIMEOUT

class SEACEScraper:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, TIMEOUT)
        self.url = URL
        self.datos_totales = []
        
    def abrir_pagina(self):
        print("Abriendo página de SEACE...")
        self.driver.get(self.url)
        time.sleep(4)
        
    def click_tab_procedimientos(self):
        print("Navegando a pestaña de Procedimientos de Selección...")
        tab = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//a[contains(@href, '#tbBuscador:tab1')]")
        ))
        tab.click()
        time.sleep(3)
        print("✓ Pestaña activa")
    
    def seleccionar_anio(self, anio):
        print(f"Seleccionando año {anio}...")
        try:
            time.sleep(2)
            select_element = self.wait.until(EC.presence_of_element_located(
                (By.ID, "tbBuscador:idFormBuscarProceso:anioConvocatoria_input")
            ))
            Select(select_element).select_by_value(str(anio))
            time.sleep(1)
            print(f"✓ Año {anio} seleccionado")
        except:
            script = f"""
            var select = document.getElementById('tbBuscador:idFormBuscarProceso:anioConvocatoria_input');
            select.value = '{anio}';
            select.dispatchEvent(new Event('change'));
            """
            self.driver.execute_script(script)
            time.sleep(1)
            print(f"✓ Año {anio} seleccionado (método alternativo)")
    
    def click_buscar(self):
        print("Ejecutando búsqueda...")
        boton = self.wait.until(EC.element_to_be_clickable(
            (By.ID, "tbBuscador:idFormBuscarProceso:btnBuscarSelToken")
        ))
        boton.click()
        time.sleep(4)
        print("✓ Búsqueda ejecutada")
    
    def esperar_resultados(self):
        self.wait.until(EC.presence_of_element_located(
            (By.ID, "tbBuscador:idFormBuscarProceso:dtProcesos_data")
        ))
        time.sleep(2)
    
    def cerrar(self):
        self.driver.quit()