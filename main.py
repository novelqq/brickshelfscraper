from bs4 import BeautifulSoup
import requests
import os
import re
import time


def write_image(imagesrc) -> None:
    cwd = os.getcwd()
    path = os.path.join(cwd, *imagesrc.split('/')[:-1])
    # print("dir path:", path)
    if not os.path.exists(path):
        os.makedirs(path)
    fpath = os.path.join(cwd, *imagesrc.split('/'))
    print("file to write: ", fpath)
    timeout_delay = 5
    retries = 0

    while True:
        try:
            print("Requesting URL: https://brickshelf.com", imagesrc.strip(" "))
            r = requests.get("https://brickshelf.com" +
                             imagesrc, stream=True, timeout=timeout_delay)
            r.raise_for_status()
            if r.status_code == 200:
                break
        except requests.exceptions.Timeout:
            print("Request timed out. Retrying...")
        except requests.exceptions.HTTPError as errh:
            print("HTTP Error")
            print(errh.args[0])
            retries += 1
            if retries > 5:
                print("failed to download file. Skipping...")
                return
        except requests.exceptions.ConnectionError as conerr:
            print("Connection error: ", conerr)
        except requests.exceptions.RequestException as err:
            print("General Error???", err, "Retrying...")

        time.sleep(timeout_delay)
        timeout_delay += 5

    length = int(r.headers['Content-length'])

    with open(fpath, 'wb') as f:
        for i, chunk in enumerate(r.iter_content(1024 * 1024)):
            print("%2.2f  percent written       \r" %
                  (i*1024*1024/length*100), end='', flush=True)
            f.write(chunk)
    print("file ", fpath, " written successfully")
    return


def write_desc(desc, img) -> None:
    cwd = os.getcwd()
    path = os.path.join(cwd, *img.split('/')[:-1])
    if not os.path.exists(path):
        os.makedirs(path)
    path = os.path.join(path, "bs_folder_description.txt")
    with open(path, 'w') as f:
        f.write(desc)
    print("file ", path, " written successfully")
    return


def find_relev_images(soup) -> list[str]:
    ret_imgs = []
    imgs = soup.find_all('a')
    # print("imgsoup: ", imgs)
    p = re.compile(r"/gallery/.+\..+")

    for img in imgs:
        m = p.match(img["href"])
        if "/cgi-bin/gallery.cgi?i=" in img['href']:
            # print("found img page: ", img['href'])
            imgsoup = soupify_link("https://brickshelf.com" + img['href'])
            imgsrc = imgsoup.find_all('img')[1]["src"]
            # print("got image src: ", imgsrc)
            ret_imgs.append(imgsrc)
        elif m is not None:
            ret_imgs.append(img['href'])
    # print("ret_imgs: ", ret_imgs)
    return ret_imgs


def soupify_link(link):
    sleeper = 1
    while True:
        try:
            r = requests.get(link, timeout=5)
            if r.status_code != 200:
                print("Error requesting link: ", link)
            else:
                break
        except requests.exceptions.Timeout:
            print("Request timed out. Retrying in ", sleeper, "s")
        except requests.exceptions.HTTPError as errh:
            print("HTTP Error")
            print(errh.args[0])
        except requests.exceptions.ConnectionError as conerr:
            print("Connection error: ", conerr)
        time.sleep(sleeper)
        sleeper += 1

    return BeautifulSoup(r.text, "html.parser")


def get_folders(soup: BeautifulSoup):
    folders = []
    for a in soup.find_all('a'):
        link = a["href"]
        if "/cgi-bin/gallery.cgi?f=" in link and str(a.string).lower() != 'up' and str(a.string).lower() != 'previous':
            folders.append("https://brickshelf.com" + link)
    return folders


def main():
    s = []
    discovered = {}

    with open("links.txt", "r") as f:
        for link in [x.strip() for x in f.readlines()]:
            s.append(link)
    print("scraping these links: ", s)
    while s:
        link = s.pop()
        if link not in discovered:
            print("new link being scraped: ", link)
            discovered[link] = 1
            soup = soupify_link(link)
            # print("calling find_relev_images...")
            images = find_relev_images(soup)
            # print("image src urls: ", images)
            desc_list = soup.find_all(attrs={"name": "description"})

            if len(desc_list) > 0 and len(images) > 0:
                write_desc(desc_list[0]["content"], images[0])

            for image in images:
                # print("attempt writing image: ", image)
                write_image(image)

            folders = get_folders(soup)
            for folder in folders:
                s.append(folder)


if __name__ == "__main__":
    main()
