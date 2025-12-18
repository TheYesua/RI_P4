"""
Módulo para cargar artículos de Wikipedia desde los archivos JSON
generados por WikiExtractor.
"""
import json
from pathlib import Path
from typing import Iterator, NamedTuple
from config import EXTRACTED_DIR


class WikiArticle(NamedTuple):
    """Representa un artículo de Wikipedia."""
    id: str
    title: str
    url: str
    text: str


def iter_wiki_articles(extracted_dir: Path = EXTRACTED_DIR, max_docs: int | None = None) -> Iterator[WikiArticle]:
    """
    Itera sobre todos los artículos de Wikipedia extraídos.
    
    WikiExtractor genera una estructura de directorios:
    extracted/
    ├── AA/
    │   ├── wiki_00
    │   ├── wiki_01
    │   └── ...
    ├── AB/
    │   └── ...
    └── ...
    
    Cada archivo wiki_XX contiene líneas JSON con formato:
    {"id": "12", "url": "https://...", "title": "...", "text": "..."}
    
    Args:
        extracted_dir: Directorio raíz de los artículos extraídos
        max_docs: Número máximo de documentos a cargar (None = todos)
    
    Yields:
        WikiArticle con id, title, url y text
    """
    if not extracted_dir.exists():
        raise FileNotFoundError(f"Directorio de extracción no encontrado: {extracted_dir}")
    
    doc_count = 0
    
    # Recorrer todos los subdirectorios (AA, AB, AC, ...)
    for subdir in sorted(extracted_dir.iterdir()):
        if not subdir.is_dir():
            continue
        
        # Recorrer todos los archivos wiki_XX en cada subdirectorio
        for wiki_file in sorted(subdir.iterdir()):
            if not wiki_file.is_file():
                continue
            
            try:
                with open(wiki_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        
                        try:
                            article = json.loads(line)
                            
                            # Filtrar artículos vacíos o muy cortos
                            text = article.get("text", "").strip()
                            if len(text) < 100:
                                continue
                            
                            yield WikiArticle(
                                id=article.get("id", ""),
                                title=article.get("title", ""),
                                url=article.get("url", ""),
                                text=text,
                            )
                            
                            doc_count += 1
                            if max_docs and doc_count >= max_docs:
                                return
                                
                        except json.JSONDecodeError:
                            continue
                            
            except Exception as e:
                print(f"Error leyendo {wiki_file}: {e}")
                continue


def count_articles(extracted_dir: Path = EXTRACTED_DIR) -> int:
    """Cuenta el número total de artículos disponibles."""
    count = 0
    for article in iter_wiki_articles(extracted_dir):
        count += 1
        if count % 100000 == 0:
            print(f"Contados {count} artículos...")
    return count


def get_article_by_id(article_id: str, extracted_dir: Path = EXTRACTED_DIR) -> WikiArticle | None:
    """
    Busca un artículo específico por su ID.
    Nota: Esta operación es O(n), para producción se debería usar un índice de metadatos.
    """
    for article in iter_wiki_articles(extracted_dir):
        if article.id == article_id:
            return article
    return None


if __name__ == "__main__":
    # Test: mostrar los primeros 5 artículos
    print("Probando carga de artículos de Wikipedia...")
    for i, article in enumerate(iter_wiki_articles(max_docs=5)):
        print(f"\n{'='*60}")
        print(f"ID: {article.id}")
        print(f"Título: {article.title}")
        print(f"URL: {article.url}")
        print(f"Texto (primeros 200 chars): {article.text[:200]}...")
