import os
import subprocess
from datetime import datetime

class GitHubUploader:
    def __init__(self, repo_path, github_user, repo_name):
        self.repo_path = repo_path
        self.github_user = github_user
        self.repo_name = repo_name
        self.docs_dir = os.path.join(repo_path, "documentos_descargados")
        
    def subir_documentos(self):
        try:
            print("\n" + "="*60)
            print("SUBIENDO DOCUMENTOS A GITHUB")
            print("="*60)
            
            os.chdir(self.repo_path)
            
            print("Agregando solo carpeta documentos_descargados...")
            result = subprocess.run(['git', 'add', 'documentos_descargados/'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Error en git add: {result.stderr}")
                return False
            print("✓ Archivos agregados")
            
            print("Creando commit...")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            commit_msg = f"Feat(docs): new docs updated - {timestamp}"
            result = subprocess.run(['git', 'commit', '-m', commit_msg], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                if "nothing to commit" in result.stdout:
                    print("⚠ No hay cambios para subir")
                    return True
                else:
                    print(f"Error en git commit: {result.stderr}")
                    return False
            print(f"✓ Commit creado: {commit_msg}")
            
            print("Subiendo a GitHub...")
            result = subprocess.run(['git', 'push'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Error en git push: {result.stderr}")
                return False
            print("✓ Documentos subidos a GitHub")
            
            print("="*60 + "\n")
            return True
            
        except Exception as e:
            print(f"Error al subir a GitHub: {e}")
            return False
    
    def generar_url_github(self, nombre_archivo):
        from urllib.parse import quote
        nombre_encoded = quote(nombre_archivo)
        return f"https://github.com/{self.github_user}/{self.repo_name}/blob/main/documentos_descargados/{nombre_encoded}"