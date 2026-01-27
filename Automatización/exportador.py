import pandas as pd
import os
from datetime import datetime
from openpyxl.styles import Font, Alignment, PatternFill

class Exportador:
    def exportar_excel(self, datos, nombre_archivo=None):
        if not datos:
            print("\n⚠ No hay datos para exportar")
            return
        
        if nombre_archivo is None:
            now = datetime.now()
            nombre_archivo = now.strftime("%m.%d.%Y") + "-T2MDC.xlsx"
        
        df_raw = pd.DataFrame(datos)
        
        fecha_extraccion = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        df_procesado = pd.DataFrame()
        
        df_procesado['Item'] = range(1, len(df_raw) + 1)
        df_procesado['Fecha de Extracción'] = fecha_extraccion
        df_procesado['Fecha y Hora de Publicacion'] = df_raw.get('Fecha y Hora de Publicacion', '')
        df_procesado['Nro de Proceso'] = df_raw.get('Nomenclatura', '')
        df_procesado['Entidad (Empresa)'] = df_raw.get('Nombre o Sigla de la Entidad', '')
        df_procesado['Tipo Servicio'] = df_raw.get('Objeto de Contratación', '')
        
        df_procesado['Registro de Participantes (Fecha fin)'] = ''
        df_procesado['Hora de Envío'] = ''
        df_procesado['Fecha de Formulacion de consultas'] = ''
        df_procesado['Fecha de integracion de bases'] = ''
        df_procesado['Presentacion de Propuesta'] = ''
        df_procesado['Hora de Envío.1'] = ''
        
        for i, dato in df_raw.iterrows():
            cronograma = dato.get('Cronograma', [])
            if isinstance(cronograma, list):
                for etapa in cronograma:
                    etapa_nombre = etapa.get('Etapa', '')
                    if 'Registro de participantes' in etapa_nombre or 'Invitación' in etapa_nombre:
                        df_procesado.at[i, 'Registro de Participantes (Fecha fin)'] = etapa.get('Fecha Fin', '')
                    elif 'Formulación de consultas' in etapa_nombre:
                        df_procesado.at[i, 'Fecha de Formulacion de consultas'] = etapa.get('Fecha Fin', '')
                    elif 'Integración de las Bases' in etapa_nombre:
                        df_procesado.at[i, 'Fecha de integracion de bases'] = etapa.get('Fecha Fin', '')
                    elif 'Presentación de propuestas' in etapa_nombre:
                        df_procesado.at[i, 'Presentacion de Propuesta'] = etapa.get('Fecha Fin', '')
        
        df_procesado['Descripción del RQ'] = df_raw.get('Descripción de Objeto', '')
        df_procesado['Documento'] = df_raw.get('Documento_Path', '')
        
        def convertir_fecha(fecha_str):
            try:
                return pd.to_datetime(fecha_str, format='%d/%m/%Y %H:%M')
            except:
                return pd.NaT
        
        df_procesado['_fecha_temp'] = df_procesado['Fecha y Hora de Publicacion'].apply(convertir_fecha)
        df_procesado = df_procesado.sort_values('_fecha_temp', ascending=False, na_position='last')
        df_procesado = df_procesado.drop('_fecha_temp', axis=1)
        df_procesado = df_procesado.reset_index(drop=True)
        df_procesado['Item'] = range(1, len(df_procesado) + 1)
        
        output_dir = "resultados_seace"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        ruta_completa = os.path.join(output_dir, nombre_archivo)
        ruta_absoluta_excel = os.path.abspath(ruta_completa)
        dir_excel = os.path.dirname(ruta_absoluta_excel)
        
        with pd.ExcelWriter(ruta_completa, engine='openpyxl') as writer:
            df_procesado.to_excel(writer, sheet_name='Procedimientos 2026', index=False)
            worksheet = writer.sheets['Procedimientos 2026']
            
            columnas_anchos = {
                'A': 8,   # Item
                'B': 22,  # Fecha de Extracción
                'C': 22,  # Fecha y Hora de Publicacion
                'D': 35,  # Nro de Proceso
                'E': 40,  # Entidad
                'F': 18,  # Tipo Servicio
                'G': 25,  # Registro Participantes
                'H': 15,  # Hora Envío
                'I': 25,  # Fecha Formulacion
                'J': 25,  # Fecha Integracion
                'K': 25,  # Presentacion Propuesta
                'L': 15,  # Hora Envío
                'M': 60,  # Descripción
                'N': 20   # Documento
            }
            
            for col, ancho in columnas_anchos.items():
                worksheet.column_dimensions[col].width = ancho
            
            header_fill = PatternFill(start_color="90EE90", end_color="90EE90", fill_type="solid")
            header_font = Font(bold=True)
            center_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            
            for cell in worksheet[1]:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = center_alignment
            
            for row in range(2, len(df_procesado) + 2):
                cell = worksheet[f'N{row}']
                doc_path = cell.value
                if doc_path and os.path.exists(doc_path):
                    ruta_absoluta_doc = os.path.abspath(doc_path)
                    cell.hyperlink = ruta_absoluta_doc
                    extension = os.path.splitext(doc_path)[1].upper()
                    cell.value = f"Ver {extension}"
                    cell.font = Font(color="0563C1", underline="single")
                    cell.alignment = Alignment(horizontal="center", vertical="center")
        
        print(f"\n{'='*60}")
        print(f"✓ EXPORTADO EXITOSAMENTE")
        print(f"{'='*60}")
        print(f"Archivo: {ruta_completa}")
        print(f"Total registros: {len(datos)}")
        print(f"Ordenado por fecha (más reciente primero)")
        print(f"{'='*60}\n")