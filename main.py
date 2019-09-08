import bs4
import re
import requests
from WikiCrop import WikiCrop
import yaml


crops_re = re.compile(r"(Spring|Summer|Fall|Special)_Crops")
harvest_re = re.compile(r"Total: (\d+) days?")
sell_re = re.compile(r"(\d+\.\d+)g")


def get_wiki_page():
    stardew_valley_wiki_url = 'https://stardewvalleywiki.com/Crops'
    print("Retrieving page at {}...".format(stardew_valley_wiki_url), sep='')
    res = requests.get(stardew_valley_wiki_url)
    # raise exception if bad request (a 4XX client error or 5XX server error response)
    print("Done")
    print("Status: {}".format(res.status_code))
    res.raise_for_status()
    print("Page size: {:.2f}KB".format(len(res.text)/1024))


def main():
    wiki_crops = []

    wiki_soup = bs4.BeautifulSoup(open("stardew_valley_wiki_crops.html"), features="html.parser")
    for elem in wiki_soup.find_all(id=crops_re):
        tag_cursor = elem.find_next("h3")
        season_name = elem.text.strip()
        while True:
            if tag_cursor is None:
                break
            crop_name_tag = tag_cursor
            crop_info_tag = crop_name_tag.find_next_sibling("table")
            tag_cursor = crop_info_tag
            tag_cursor = tag_cursor.find_next_sibling(re.compile(r'h[23]'))

            crop_name = crop_name_tag.text.strip()
            if crop_name in ["Mixed Seeds", "Wild Seeds"]:  # skip these
                continue
            crop_obj = WikiCrop(crop_name, season_name)
            crop_obj.table_to_data(crop_info_tag)
            wiki_crops.append(crop_obj)
            if tag_cursor.name == "h2":
                break

    for crop in wiki_crops:
        print(crop)


if __name__ == '__main__':
    main()
