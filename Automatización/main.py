from scraper import SEACEScraper
from extractor import Extractor
from navegador import Navegador
from navegador_ficha import NavegadorFicha
from extractor_ficha import ExtractorFicha
from exportador import Exportador
from filtros import Filtros
from config import ANIOS

def main():
    scraper = SEACEScraper()
    3
    try:
        scraper.abrir_pagina()
        scraper.click_tab_procedimientos()
        
        extractor = Extractor(scraper.driver)
        navegador = Navegador(scraper.driver)
        nav_ficha = NavegadorFicha(scraper.driver)
        ext_ficha = ExtractorFicha(scraper.driver)
        
        nav_ficha.guardar_ventana_principal()
        datos_totales = []
        
        for anio in ANIOS:
            print(f"\n{'='*60}")
            print(f"PROCESANDO AÑO {anio}")
            print(f"{'='*60}")
            
            scraper.seleccionar_objeto_contratacion()
            scraper.seleccionar_anio(anio)
            scraper.click_buscar()
            scraper.esperar_resultados()
            
            pagina_actual, total_paginas = extractor.obtener_info_paginacion()
            print(f"Total páginas: {total_paginas}")
            
            for num_pagina in range(1, total_paginas + 1):
                print(f"\n{'─'*60}")
                print(f"Página {num_pagina}/{total_paginas}")
                print(f"{'─'*60}")
                
                datos_pagina = extractor.extraer_datos_pagina()
                datos_filtrados = Filtros.filtrar_datos(datos_pagina)
                
                print(f"Total: {len(datos_pagina)} | Filtrados: {len(datos_filtrados)}")
                
                for idx, dato in enumerate(datos_filtrados):
                    print(f"  [{idx+1}/{len(datos_filtrados)}] {dato['Nomenclatura']}")
                    
                    if nav_ficha.click_ficha_seleccion(dato['Indice']):
                        info_ficha = ext_ficha.extraer_todo()
                        dato.update(info_ficha)
                        nav_ficha.click_regresar()
                    
                    del dato['Indice']
                    datos_totales.append(dato)
                
                print(f"✓ Página {num_pagina} completada ({len(datos_totales)} registros acumulados)")
                
                if num_pagina < total_paginas:
                    print(f"→ Navegando a página {num_pagina + 1}...")
                    if not navegador.click_numero_pagina(num_pagina + 1):
                        print("  Intento 1 falló, probando botón siguiente...")
                        if not navegador.ir_siguiente_pagina():
                            print("  ⚠ No se pudo navegar, deteniendo...")
                            break
                    else:
                        print(f"  ✓ En página {num_pagina + 1}")
        
        print(f"\n{'='*60}")
        print(f"RESUMEN FINAL")
        print(f"{'='*60}")
        print(f"Total registros filtrados: {len(datos_totales)}")
        
        exportador = Exportador()
        exportador.exportar_excel(datos_totales)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\nCerrando navegador...")
        scraper.cerrar()

if __name__ == "__main__":
    main()