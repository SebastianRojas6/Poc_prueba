from selenium.webdriver.common.by import By

class Extractor:
    def __init__(self, driver):
        self.driver = driver
    
    def extraer_datos_pagina(self):
        tabla = self.driver.find_element(By.ID, "tbBuscador:idFormBuscarProceso:dtProcesos_data")
        filas = tabla.find_elements(By.TAG_NAME, "tr")
        datos = []
        for i, fila in enumerate(filas):
            try:
                celdas = fila.find_elements(By.TAG_NAME, "td")
                if len(celdas) >= 13:
                    dato = {
                        'Indice': i,
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
                        datos.append(dato)
            except:
                continue
        return datos
    
    def obtener_info_paginacion(self):
        try:
            paginador = self.driver.find_element(By.ID, 
                "tbBuscador:idFormBuscarProceso:dtProcesos_paginator_bottom")
            span = paginador.find_element(By.CLASS_NAME, "ui-paginator-current")
            texto = span.text
            if "Página:" in texto:
                partes = texto.split("Página:")[1].strip().rstrip("]").strip()
                pagina_actual, total_paginas = partes.split("/")
                return int(pagina_actual), int(total_paginas)
        except:
            return 1, 1
        return 1, 1