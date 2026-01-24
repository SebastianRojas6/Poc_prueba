from config import PALABRAS_CLAVE

class Filtros:
    @staticmethod
    def contiene_palabra_clave(texto):
        texto_lower = texto.lower()
        for palabra in PALABRAS_CLAVE:
            if palabra.lower() in texto_lower:
                return True
        return False
    
    @staticmethod
    def filtrar_datos(datos):
        return [d for d in datos if Filtros.contiene_palabra_clave(d.get('Descripción de Objeto', ''))]