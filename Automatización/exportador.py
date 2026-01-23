# exportador.py
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
        
        df = pd.DataFrame(datos)
        output_dir = "resultados_seace"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        ruta_completa = os.path.join(output_dir, nombre_archivo)
        
        with pd.ExcelWriter(ruta_completa, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Procedimientos 2026', index=False)
            worksheet = writer.sheets['Procedimientos 2026']
            for i, col in enumerate(df.columns):
                max_length = max(df[col].astype(str).map(len).max(), len(col)) + 2
                col_letter = chr(65 + i) if i < 26 else chr(65 + i//26 - 1) + chr(65 + i%26)
                worksheet.column_dimensions[col_letter].width = min(max_length, 50)
        
        print(f"\n{'='*60}")
        print(f"✓ EXPORTADO EXITOSAMENTE")
        print(f"{'='*60}")
        print(f"Archivo: {ruta_completa}")
        print(f"Total registros: {len(datos)}")
        print(f"{'='*60}\n")