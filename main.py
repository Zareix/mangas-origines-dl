"""Download all chapters of a manga from a given manga-origines.fr URL"""

import os
import shutil
from zipfile import ZipFile
import re
import time
from tqdm import tqdm
from bs4 import BeautifulSoup
import cloudscraper

CHAPTER_OFFSET = 0
WORK_DIR = "./work"
OUTPUT_DIR = "./output"


def download_chapter(scraper, base_url, chapter_num):
    """Download a specific chapter"""
    chapter_url = (
        re.sub(r"chapitre-\d+", f"chapitre-{chapter_num}", base_url).split("?")[0]
        + "?style=list"
    )

    try:
        print(f"\nTéléchargement du chapitre {chapter_num}...")
        soup = BeautifulSoup(scraper.get(chapter_url).text, "html.parser")

        manga_title = (
            soup.find("ol", class_="breadcrumb").find_all("li")[-2].text.strip()
        )
        pages = soup.find_all("img", "wp-manga-chapter-img")

        if not pages:
            print(f"Aucune page trouvée pour le chapitre {chapter_num}")
            return False

        nbpage = int(len(pages))
        titles = []

        # Create directory for this chapter inside WORK_DIR
        chapterNumber = f"Ch.{chapter_num + CHAPTER_OFFSET}"
        chapter_dir = os.path.join(WORK_DIR, f"{manga_title} {chapterNumber}")
        if not os.path.exists(chapter_dir):
            os.makedirs(chapter_dir)

        # Download all pages
        with tqdm(total=nbpage) as pbar:
            pbar.set_description(
                f"Téléchargement de {nbpage} page(s) - Chapitre {chapter_num}"
            )
            for pageNum, page in enumerate(pages, 1):
                try:
                    file_path = os.path.join(chapter_dir, f"{pageNum}.jpg")
                    with open(file_path, "wb") as handler:
                        titles.append(file_path)
                        handler.write(scraper.get(page["src"]).content)
                        pbar.update(1)
                except Exception as e:
                    print(f"Erreur lors du téléchargement de la page {pageNum}: {e}")
                    continue

        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)

        # Create CBZ file
        cbz_filename = os.path.join(OUTPUT_DIR, f"{manga_title} {chapterNumber}.cbz")
        with tqdm(total=len(titles)) as pbar:
            pbar.set_description(f'Création de "{os.path.basename(cbz_filename)}"')
            with ZipFile(cbz_filename, "w") as myzip:
                for title in titles:
                    myzip.write(title, arcname=os.path.basename(title))
                    pbar.update(1)

        # Clean up temporary directory
        shutil.rmtree(chapter_dir)
        print(f"Chapitre {chapter_num} téléchargé avec succès!")
        return True

    except Exception as e:
        print(f"Erreur lors du téléchargement du chapitre {chapter_num}: {e}")
        return False


def main():
    """Main function to download all chapters from a given URL"""
    scraper = cloudscraper.create_scraper()

    # Get URL and last chapter from user
    base_url = input("URL du premier chapitre : ")
    last_chapter = int(input("Numéro du dernier chapitre : "))

    # Extract chapter number from URL
    chapter_match = re.search(r"chapitre-(\d+)", base_url)
    if not chapter_match:
        print("Impossible d'extraire le numéro de chapitre de l'URL")
        return

    start_chapter = int(chapter_match.group(1))

    print(f"Téléchargement des chapitres {start_chapter} à {last_chapter}")

    successful_downloads = 0
    failed_downloads = 0

    for chapter_num in range(start_chapter, last_chapter + 1):
        success = download_chapter(scraper, base_url, chapter_num)
        if success:
            successful_downloads += 1
        else:
            failed_downloads += 1
            if failed_downloads >= 3:
                print("Trop d'échecs consécutifs, arrêt du téléchargement.")
                break

        time.sleep(1)

    print("\nTéléchargement terminé!")
    print(f"Chapitres téléchargés avec succès: {successful_downloads}")
    print(f"Chapitres échoués: {failed_downloads}")

if __name__ == "__main__":
    main()
