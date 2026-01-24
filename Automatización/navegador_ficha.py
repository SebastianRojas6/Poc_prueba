from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class NavegadorFicha:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 30)
        self.ventana_principal = None
    
    def guardar_ventana_principal(self):
        self.ventana_principal = self.driver.current_window_handle
    
    def click_ficha_seleccion(self, indice):
        try:
            tabla = self.driver.find_element(By.ID, "tbBuscador:idFormBuscarProceso:dtProcesos_data")
            filas = tabla.find_elements(By.TAG_NAME, "tr")
            
            if indice >= len(filas):
                print(f"    Error: índice {indice} fuera de rango (total filas: {len(filas)})")
                return False
            
            fila = filas[indice]
            data_ri = fila.get_attribute("data-ri")
            
            ficha_id = f"tbBuscador:idFormBuscarProceso:dtProcesos:{data_ri}:j_idt377"
            
            elemento = self.wait.until(EC.presence_of_element_located(
                (By.ID, ficha_id)
            ))
            
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elemento)
            time.sleep(1)
            
            try:
                self.driver.execute_script("arguments[0].click();", elemento)
            except:
                elemento.click()
            
            time.sleep(5)
            return True
        except Exception as e:
            print(f"    Error al abrir ficha: {e}")
            return False
    
    def click_regresar(self):
        try:
            print("    Haciendo clic en Regresar...")
            boton = self.wait.until(EC.element_to_be_clickable(
                (By.ID, "tbFicha:j_idt746")
            ))
            boton.click()
            time.sleep(4)
            
            self.wait.until(EC.presence_of_element_located(
                (By.ID, "tbBuscador:idFormBuscarProceso:dtProcesos_data")
            ))
            time.sleep(2)
            print("    ✓ Regresó a lista de resultados")
        except Exception as e:
            print(f"    Error en regresar: {e}")