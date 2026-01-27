import os
from scraper import SEACEScraper
from extractor import Extractor
from navegador import Navegador
from navegador_ficha import NavegadorFicha
from extractor_ficha import ExtractorFicha
from exportador import Exportador
from filtros import Filtros
from github_uploader import GitHubUploader
from config import ANIOS, LIMITE_PAGINAS, GITHUB_USER, GITHUB_REPO, REPO_PATH

def main():
    scraper = SEACEScraper()
    
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
            print(f"Procesando solo {LIMITE_PAGINAS} página(s) para prueba")
            
            for num_pagina in range(1, min(LIMITE_PAGINAS + 1, total_paginas + 1)):
                print(f"\n{'─'*60}")
                print(f"Página {num_pagina}/{total_paginas}")
                print(f"{'─'*60}")
                
                datos_pagina = extractor.extraer_datos_pagina()
                datos_filtrados = Filtros.filtrar_datos(datos_pagina)
                
                print(f"Total: {len(datos_pagina)} | Filtrados: {len(datos_filtrados)}")
                
                for idx, dato in enumerate(datos_filtrados):
                    print(f"  [{idx+1}/{len(datos_filtrados)}] {dato['Nomenclatura']}")
                    
                    if nav_ficha.click_ficha_seleccion(dato['Indice']):
                        info_ficha = ext_ficha.extraer_todo(dato['Nomenclatura'])
                        dato.update(info_ficha)
                        nav_ficha.click_regresar()
                    
                    del dato['Indice']
                    datos_totales.append(dato)
                
                print(f"✓ Página {num_pagina} completada ({len(datos_totales)} registros acumulados)")
        
        print(f"\n{'='*60}")
        print(f"RESUMEN FINAL")
        print(f"{'='*60}")
        print(f"Total registros filtrados: {len(datos_totales)}")
        
        github = GitHubUploader(REPO_PATH, GITHUB_USER, GITHUB_REPO)
        
        for dato in datos_totales:
            if dato.get('Documento_Path'):
                nombre_archivo = os.path.basename(dato['Documento_Path'])
                dato['Documento_URL'] = github.generar_url_github(nombre_archivo)
        
        exportador = Exportador()
        exportador.exportar_excel(datos_totales)
        
        github.subir_documentos()
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\nCerrando navegador...")
        scraper.cerrar()

if __name__ == "__main__":
    main()