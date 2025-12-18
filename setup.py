"""
Script de configuracion automatica del proyecto WikiSearch.

Ejecutar desde la raiz del proyecto:
    python setup.py

Este script:
1. Verifica Python 3.11+
2. Instala dependencias del backend (pip)
3. Descarga recursos de NLTK
4. Instala dependencias del frontend (npm)
5. Muestra instrucciones para construir el indice
"""
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], cwd: Path | None = None, check: bool = True) -> bool:
    """Ejecuta un comando y muestra su salida."""
    print(f"\n> {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, cwd=cwd, check=check)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Comando fallo con codigo {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"[ERROR] Comando no encontrado: {cmd[0]}")
        return False


def check_python_version() -> bool:
    """Verifica que Python sea 3.11+."""
    print("\n" + "=" * 60)
    print("[1/5] Verificando version de Python...")
    print("=" * 60)
    
    version = sys.version_info
    print(f"  Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print("[ERROR] Se requiere Python 3.11 o superior")
        return False
    
    print("  [OK] Version compatible")
    return True


def install_backend_deps(project_root: Path) -> bool:
    """Instala dependencias del backend con pip."""
    print("\n" + "=" * 60)
    print("[2/5] Instalando dependencias del backend...")
    print("=" * 60)
    
    requirements = project_root / "backend" / "requirements.txt"
    if not requirements.exists():
        print(f"[ERROR] No se encontro {requirements}")
        return False
    
    return run_command([sys.executable, "-m", "pip", "install", "-r", str(requirements)])


def download_nltk_data() -> bool:
    """Descarga recursos necesarios de NLTK."""
    print("\n" + "=" * 60)
    print("[3/5] Descargando recursos de NLTK...")
    print("=" * 60)
    
    try:
        import nltk
        
        resources = ['punkt', 'stopwords', 'punkt_tab']
        for resource in resources:
            print(f"  Descargando {resource}...")
            nltk.download(resource, quiet=True)
        
        print("  [OK] Recursos NLTK descargados")
        return True
    except Exception as e:
        print(f"[ERROR] Fallo al descargar NLTK: {e}")
        return False


def check_npm() -> bool:
    """Verifica si npm esta disponible."""
    try:
        result = subprocess.run(
            ["npm", "--version"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def install_frontend_deps(project_root: Path) -> bool:
    """Instala dependencias del frontend con npm."""
    print("\n" + "=" * 60)
    print("[4/5] Instalando dependencias del frontend...")
    print("=" * 60)
    
    frontend_dir = project_root / "frontend"
    if not (frontend_dir / "package.json").exists():
        print(f"[ERROR] No se encontro package.json en {frontend_dir}")
        return False
    
    if not check_npm():
        print("[WARN] npm no encontrado. Opciones:")
        print("  1. Instalar Node.js desde https://nodejs.org")
        print("  2. O ejecutar: conda install nodejs -c conda-forge")
        print("  Luego ejecutar manualmente: cd frontend && npm install")
        return False
    
    return run_command(["npm", "install"], cwd=frontend_dir)


def show_next_steps(project_root: Path) -> None:
    """Muestra los siguientes pasos."""
    print("\n" + "=" * 60)
    print("[5/5] Configuracion completada")
    print("=" * 60)
    
    print("""
Siguientes pasos:

1. CONSTRUIR EL INDICE (necesario antes de buscar):
   cd backend
   python build_index.py
   
   Nota: Para prueba rapida usar --max-docs 10000

2. INICIAR EL BACKEND:
   cd backend
   uvicorn main:app --reload
   
   API disponible en: http://localhost:8000

3. INICIAR EL FRONTEND:
   cd frontend
   npm run dev
   
   Interfaz disponible en: http://localhost:5173
""")


def main():
    print("=" * 60)
    print("CONFIGURACION DE WIKISEARCH")
    print("Sistema de Recuperacion de Informacion")
    print("=" * 60)
    
    project_root = Path(__file__).parent
    
    # Paso 1: Verificar Python
    if not check_python_version():
        sys.exit(1)
    
    # Paso 2: Instalar dependencias backend
    if not install_backend_deps(project_root):
        print("\n[ERROR] Fallo la instalacion del backend")
        sys.exit(1)
    
    # Paso 3: Descargar NLTK
    if not download_nltk_data():
        print("\n[WARN] Fallo la descarga de NLTK, continuar manualmente")
    
    # Paso 4: Instalar dependencias frontend
    if not install_frontend_deps(project_root):
        print("\n[WARN] Frontend no configurado, instalar npm manualmente")
    
    # Paso 5: Mostrar siguientes pasos
    show_next_steps(project_root)


if __name__ == "__main__":
    main()
