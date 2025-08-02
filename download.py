import os
import shutil
from zipfile import ZipFile
import cloudscraper
from tqdm import tqdm
from bs4 import BeautifulSoup

inputUrl = (
    input("URL : ").replace("?style=paged", "").replace("?style=list", "")
    + "?style=list"
)
scraper = cloudscraper.create_scraper()
r = scraper.get(inputUrl).text

soup = BeautifulSoup(r, "html.parser")

pageNum = 0

manga_title = soup.find("ol", class_="breadcrumb").find_all("li")[-2].text.strip()
chapNumber = "Ch." + input("Chap number : ")
pages = soup.find_all("img", "wp-manga-chapter-img")
nbpage = int(len(pages))

titles = []

if not os.path.exists(f"./{manga_title} {chapNumber}"):
    os.makedirs(f"./{manga_title} {chapNumber}")

with tqdm(total=nbpage) as pbar:
    pbar.set_description(f"Téléchargement de {nbpage} page(s)")
    for page in pages:
        img_data = scraper.get(page["src"]).content
        pageNum = pageNum + 1
        with open(f"./{manga_title} {chapNumber}/{pageNum}.jpg", "wb") as handler:
            titles.append(f"./{manga_title} {chapNumber}/{pageNum}.jpg")
            handler.write(img_data)
            pbar.update(1)
with tqdm(total=nbpage) as pbar:
    pbar.set_description(f'Création de "{manga_title} {chapNumber}.cbz"')
    with ZipFile(f"{manga_title} {chapNumber}.cbz", "w") as myzip:
        for title in titles:
            myzip.write(title)
            pbar.update(1)

shutil.rmtree(f"./{manga_title} {chapNumber}")
