from scraper import SEACEScraper
from extractor import Extractor
from navegador import Navegador
from exportador import Exportador
from config import ANIOS

def main():
    scraper = SEACEScraper()
    
    try:
        scraper.abrir_pagina()
        scraper.click_tab_procedimientos()
        
        extractor = Extractor(scraper.driver)
        navegador = Navegador(scraper.driver)
        datos_totales = []
        
        for anio in ANIOS:
            print(f"\n{'='*60}")
            print(f"PROCESANDO AÑO {anio}")
            print(f"{'='*60}")
            
            scraper.seleccionar_anio(anio)
            scraper.click_buscar()
            scraper.esperar_resultados()
            
            pagina_actual, total_paginas = extractor.obtener_info_paginacion()
            print(f"Total páginas: {total_paginas}")
            
            for num_pagina in range(1, total_paginas + 1):
                print(f"Página {num_pagina}/{total_paginas}")
                datos = extractor.extraer_datos_pagina()
                if datos:
                    datos_totales.extend(datos)
                    print(f"✓ {len(datos)} registros")
                
                if num_pagina < total_paginas:
                    if not navegador.click_numero_pagina(num_pagina + 1):
                        if not navegador.ir_siguiente_pagina():
                            break
        
        exportador = Exportador()
        exportador.exportar_excel(datos_totales)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        scraper.cerrar()

if __name__ == "__main__":
    main()