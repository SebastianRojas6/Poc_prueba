import pandas as pd
import os
from datetime import datetime

class Exportador:
    def exportar_excel(self, datos, nombre_archivo=None):
        if not datos:
            print("\n⚠ No hay datos para exportar")
            return
        
        if nombre_archivo is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"SEACE_2026_{timestamp}.xlsx"
        
        df_raw = pd.DataFrame(datos)
        
        df_procesado = pd.DataFrame()
        
        df_procesado['Item'] = range(1, len(df_raw) + 1)
        df_procesado['Nro de Proceso'] = df_raw.get('Nomenclatura', '')
        df_procesado['Entidad (Empresa)'] = df_raw.get('Nombre o Sigla de la Entidad', '')
        df_procesado['Tipo Servicio'] = df_raw.get('Objeto de Contratación', '')
        
        cronogramas = df_raw.get('Cronograma', [])
        for i, dato in df_raw.iterrows():
            cronograma = dato.get('Cronograma', [])
            if isinstance(cronograma, list):
                for etapa in cronograma:
                    if 'Registro de participantes' in etapa.get('Etapa', ''):
                        df_procesado.at[i, 'Registro de Participantes (Fecha fin)'] = etapa.get('Fecha Fin', '')
                        df_procesado.at[i, 'Hora de Envío'] = ''
                    elif 'Formulación de consultas' in etapa.get('Etapa', ''):
                        df_procesado.at[i, 'Fecha de Formulacion de consultas'] = etapa.get('Fecha Fin', '')
                    elif 'Integración de las Bases' in etapa.get('Etapa', ''):
                        df_procesado.at[i, 'Fecha de integracion de bases'] = etapa.get('Fecha Fin', '')
                    elif 'Presentación de propuestas' in etapa.get('Etapa', ''):
                        df_procesado.at[i, 'Presentacion de Propuesta'] = etapa.get('Fecha Fin', '')
                        df_procesado.at[i, 'Hora de Envío'] = ''
        
        df_procesado['Descripción del RQ'] = df_raw.get('Descripción de Objeto', '')
        
        output_dir = "resultados_seace"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        ruta_completa = os.path.join(output_dir, nombre_archivo)
        
        with pd.ExcelWriter(ruta_completa, engine='openpyxl') as writer:
            df_procesado.to_excel(writer, sheet_name='Procedimientos 2026', index=False)
            worksheet = writer.sheets['Procedimientos 2026']
            
            columnas_anchos = {
                'A': 8,   # Item
                'B': 35,  # Nro de Proceso
                'C': 40,  # Entidad
                'D': 18,  # Tipo Servicio
                'E': 25,  # Registro Participantes
                'F': 15,  # Hora Envío
                'G': 25,  # Fecha Formulacion
                'H': 25,  # Fecha Integracion
                'I': 25,  # Presentacion Propuesta
                'J': 15,  # Hora Envío
                'K': 60   # Descripción
            }
            
            for col, ancho in columnas_anchos.items():
                worksheet.column_dimensions[col].width = ancho
            
            from openpyxl.styles import Font, Alignment, PatternFill
            
            header_fill = PatternFill(start_color="90EE90", end_color="90EE90", fill_type="solid")
            header_font = Font(bold=True)
            center_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            
            for cell in worksheet[1]:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = center_alignment
        
        print(f"\n{'='*60}")
        print(f"✓ EXPORTADO EXITOSAMENTE")
        print(f"{'='*60}")
        print(f"Archivo: {ruta_completa}")
        print(f"Total registros: {len(datos)}")
        print(f"{'='*60}\n")