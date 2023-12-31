import time
import re
from typing import List
import json
import numpy as np
from model import Website, Crawler, Driver, get_info_site, Content
from lxml import etree

import bs4

info_site = get_info_site(site="cdiscount", device="desktop")

cdiscount = Website(
    name=info_site.get("name"),
    url=info_site.get("url"),
    target_pattern=info_site.get("target_pattern"),
    absolute_url=info_site.get("absolute_url"),
    tags=info_site.get("tags"),
    patterns=info_site.get("patterns"),
    groups=info_site.get("groups"),
    tags_get_from_seller_listing=info_site.get("tags_get_from_seller_listing"),
)
# regex permettant de trouver si il y a d'autre vendeurs.
# //a[@rel="noindex, nofollow"]

# regex permettant de trouver la page des autre vendeurs.
# //a[@class="slrName"]//@href

# regex permettant de trouver tous les produits sur la page d'un vendeur.
# //li[@data-sku]//a[@href]

# regex dans lequel sont stockés les liens des sites des produits sur la page d'accueil.
# url = "https://www.cdiscount.com/electromenager/aspirateurs-nettoyeurs/karcher-vc6-our-family-aspirateur-balai-multifon/f-1101410-kar4054278834221.html?idOffre=1884935695#mpos=0|mp"

# url_other_seller = "https://www.cdiscount.com/mp-53739-kar4054278834221.html?Filter=New"
# tmp = crawler.get_page(url)
# tmp_other_seller = crawler.get_page(url_other_seller)
# dom = etree.HTML(str(tmp))

"-------------------------------------------------------------------"


def safe_get(page_obj: bs4.BeautifulSoup, selector: str) -> str:
    selected_elems = etree.HTML(str(page_obj)).xpath(selector)
    if selected_elems is not None and len(selected_elems) > 0:
        try:
            return "\n".join([elem.text.strip() for elem in selected_elems])
        except Exception as e:
            return "\n".join([elem for elem in selected_elems])
    return ""


# Traitement des cas sans ean comme les produits pas encore en ventes mais bientôt en ventes.
# Traitement des as vendus par cdiscount
# script dans la page produit (//script[@type="application/ld+json"])
# selected_elems = etree.HTML(str(tmp_other_seller)).xpath('//div[@class="fpBlk fpTab"]//text()')
# selected_elems = etree.HTML(str(tmp)).xpath("//*[contains(text(),'pr_ean')]")
# r = crawler.safe_get(tmp_other_seller,'//div[@class="fpBlk fpTab"]//text()')
# get_link_home_page = crawler.safe_get(tmp_home_page,'//a[@class="o-card__link flow--xs"]')


"-------------------------------------------------------------------"


def parse_seller_listing_page(bs: str) -> List[dict]:
    """_summary_

    Args:
        bs (str): _description_

    Returns:
        List[dict]: _description_
    """

    tag_from_listing_page_raw_data = {
        tag: get_safe_pattern(
            bs,
            info_site["patterns"].get(tag),
            info_site["groups"].get(tag),
        )
        for tag in info_site["tags_get_from_seller_listing"]
    }
    offers = [
        {
            tag: tag_from_listing_page_raw_data[tag][seller_iterator].replace("\n", "")
            for tag in tag_from_listing_page_raw_data.keys()
        }
        for seller_iterator in range(len(tag_from_listing_page_raw_data["seller_name"]))
    ]
    return offers


# parse_seller_listing_page(tmp_page_from_home_page)
# tmp3 = crawler.parse_seller_listing_page(tmp_other_seller)

"-------------------------------------------------------------------"

"""get_safe_pattern(r, "(.*\n.*)(?=Disponibilité)(.*)", 0)
get_safe_pattern(r, "(\d+\n€\d+)(.*)", 0)
get_safe_pattern(r, "(.*\n.)(\n.*)(\d+\n€\d+)", 0)
get_safe_pattern(r, "(Expédié par :)\n(.*)", 1)
get_safe_pattern(r, "Cdiscount|Ventes réalisées :(\n.*\d+)(.*)", 0)
get_safe_pattern(r, "(.*\n)(.*\n.*)(?=Disponibilité)", 0)
get_safe_pattern(r, "Cdiscount|(Évaluation(.*)\n(.*))", 0)
get_safe_pattern(r1)"""


def get_safe_pattern(selected_tag: str, pattern: str = "(.*)", group: int = 0) -> str:
    pattern = pattern or "(.*)"
    group = group or 0
    try:
        elems = [
            captured_elem[group].strip()
            for captured_elem in re.findall(pattern, selected_tag)
        ]
    except IndexError:
        elems = re.findall(pattern, selected_tag)[group]
    if len(elems) < 2:
        return "".join(elems)
    return elems


"-------------------------------------------------------------------"

crawler = Crawler(cdiscount)
url_home_page = "https://www.cdiscount.com/"
tmp_home_page = crawler.get_page(url_home_page)


def list_url_from_home_page(tmp_home_page):
    all_link_home_page = []
    raw_link = etree.HTML(str(tmp_home_page)).xpath(info_site["link_product_home_page"])
    for ele in raw_link:
        all_link_home_page.append(ele.values()[1])
    return all_link_home_page


def raw_info_extracted(info_site, crawler, tmp_page_from_home_page):
    raw_all_info_page_from_home_page = {}
    for name, tag in info_site["tags"].items():
        try:
            crawler.safe_get(tmp_page_from_home_page, tag)
            raw_all_info_page_from_home_page[name] = crawler.safe_get(
                tmp_page_from_home_page, tag
            )
        except Exception:
            pass
    return raw_all_info_page_from_home_page


def extract_info_page_from_home_page(info_site, crawler, tmp_page_from_home_page):
    raw_all_info_page_from_home_page = raw_info_extracted(
        info_site, crawler, tmp_page_from_home_page
    )
    all_info_page_from_home_page = {}
    for label, info in raw_all_info_page_from_home_page.items():
        if info != "":
            all_info_page_from_home_page[label] = info
        if (info == "") and (label == "seller_name"):
            all_info_page_from_home_page[label] = "Cdiscount"
    return all_info_page_from_home_page


def formatting_info_page_from_home_page(
    info_site, get_safe_pattern, all_info_page_from_home_page
):
    cp = all_info_page_from_home_page.copy()
    for label_tag, raw_tag in cp.items():
        for label_regex, regex in info_site["patterns"].items():
            if label_tag == label_regex:
                info_extracted = get_safe_pattern(
                    raw_tag, regex, info_site["groups"][label_regex]
                ).replace("\n", "")
                cp[label_tag] = info_extracted
    return cp


def add_relative_url_other_seller(list_all_info_other_seller, url_other_seller):
    for ele in list_all_info_other_seller:
        for url in url_other_seller:
            if ele["seller_name"] in url:
                ele["url_relative_seller"] = url


def check_if_relative_url_other_seller_was_visited(
    link_page_seller_no_visited, link_page_seller_visited, url_other_seller
):
    for relative_url in url_other_seller:
        if relative_url not in link_page_seller_visited:
            link_page_seller_no_visited.add(relative_url)


def extract_url_top_product_from_seller_page(list_raw_url_product_from_seller_page):
    list_url_top_product_from_seller_page = []
    for ele in list_raw_url_product_from_seller_page:
        if ("https" in ele) and ("f-" in ele):
            list_url_top_product_from_seller_page.append(ele)
        else:
            pass
    return list_url_top_product_from_seller_page


def add_url_top_product(
    link_find_no_visited, link_find_visited_url, list_url_top_product_from_seller_page
):
    for url_product in list_url_top_product_from_seller_page:
        if url_product not in link_find_visited_url:
            link_find_no_visited.append(url_product)


def extract_top_product_from_url_seller(
    info_site,
    crawler,
    url_home_page,
    extract_url_top_product_from_seller_page,
    add_url_top_product,
    link_find_no_visited,
    link_find_visited_url,
    link_page_seller_no_visited,
    link_page_seller_visited,
):
    cp_link_page_seller_no_visited = link_page_seller_no_visited.copy()
    for page_seller in link_page_seller_no_visited:
        url_seller_page = url_home_page + page_seller
        tmp_page_seller = crawler.get_page(url_seller_page)
        list_raw_url_product_from_seller_page = etree.HTML(str(tmp_page_seller)).xpath(
            info_site["tags_page_seller"]["url_page_seller"]
        )

        list_url_top_product_from_seller_page = (
            extract_url_top_product_from_seller_page(
                list_raw_url_product_from_seller_page
            )
        )
        link_page_seller_visited.add(url_seller_page)
        cp_link_page_seller_no_visited.remove(page_seller)
        add_url_top_product(
            link_find_no_visited,
            link_find_visited_url,
            list_url_top_product_from_seller_page,
        )
    link_page_seller_no_visited = cp_link_page_seller_no_visited
    return link_page_seller_no_visited


all_link_home_page = list_url_from_home_page(tmp_home_page)
link_find_no_visited = [*set(all_link_home_page)]
link_find_visited_ean = set()
link_find_visited_url = set()
link_page_seller_no_visited = set()
link_page_seller_visited = set()
info_products = {}

start = time.time()
t = np.random.uniform(0.1, 4)
time.sleep(t)

for link in link_find_no_visited[:2]:
    time.sleep(t)
    url_page_from_home_page = link
    tmp_page_from_home_page = crawler.get_page(url_page_from_home_page)
    all_info_raw_product_from_home_page = extract_info_page_from_home_page(
        info_site, crawler, tmp_page_from_home_page
    )
    info_page_formatted = formatting_info_page_from_home_page(
        info_site, get_safe_pattern, all_info_raw_product_from_home_page
    )
    link_find_visited_ean.add(info_page_formatted["ean"])
    link_find_visited_url.add(url_page_from_home_page)
    index = link_find_no_visited.index(url_page_from_home_page)
    link_find_no_visited.pop(index)
    try:
        url_other_product_from_page_product = (
            url_home_page + info_page_formatted["seller_listing"][1:]
        )
        tmp_all_other_seller_page = crawler.get_page(
            url_other_product_from_page_product
        )
        bs_product_other_seller = crawler.safe_get(
            tmp_all_other_seller_page, '//div[@class="fpBlk fpTab"]//text()'
        )
        list_all_info_other_seller = parse_seller_listing_page(bs_product_other_seller)
        url_other_seller = crawler.safe_get(
            tmp_all_other_seller_page, '//a[@class="slrName"]//@href'
        ).split("\n")
        add_relative_url_other_seller(list_all_info_other_seller, url_other_seller)
        check_if_relative_url_other_seller_was_visited(
            link_page_seller_no_visited, link_page_seller_visited, url_other_seller
        )
        info_page_formatted["info_other_seller"] = list_all_info_other_seller
        info_products[info_page_formatted["ean"]] = info_page_formatted
        link_page_seller_no_visited = extract_top_product_from_url_seller(
            info_site,
            crawler,
            url_home_page,
            extract_url_top_product_from_seller_page,
            add_url_top_product,
            link_find_no_visited,
            link_find_visited_url,
            link_page_seller_no_visited,
            link_page_seller_visited,
        )
    except Exception:
        info_products[info_page_formatted["ean"]] = info_page_formatted
        try:
            info_page_formatted["page_seller"]
            if info_page_formatted["page_seller"] not in link_page_seller_visited:
                link_page_seller_no_visited.add(info_page_formatted["page_seller"])
        except Exception:
            pass
end = time.time()


start1 = time.time()
json_object = json.dumps(info_products, indent=2)
jsonFile = open("all_info_product.json", "w")
jsonFile.write(json_object)
jsonFile.close()

end1 = time.time()

print((end - start) / 60)
print(end1 - start1)

"-------------------------------------------------------------------"

"""
def parse_seller_listing_page(self, url: str) -> dict:
    # TODO: check if it is absolute url or not
    bs = self.get_page(url)
    if bs is not None:
        for tag_name, tag_attr in self.tags.items():
            raw_elmt = self.safe_get(bs, tag_attr)
            self.data[tag_name] = self.get_safe_pattern(
                raw_elmt, self.patterns.get(tag_name), self.groups.get(tag_name)
            )
        self.data["timestamp"] = int(time.time())
        self.data["url"] = url



def is_absolute_url():
    pass


def parse(self, url: str) -> dict:
    bs = self.get_page(url)
    raw_data = {"offers": []}
    if bs is not None:
        for tag_name, tag_attr in self.website_info.tags.items():
            if tag_name in ["title", "ean", "url"]:
                raw_elmt = self.safe_get(bs, tag_attr)
                raw_data[tag_name] = self.get_safe_pattern(
                    raw_elmt, self.patterns.get(tag_name), self.groups.get(tag_name)
                )
                raw_data["timestamp"] = int(time.time())
            else:
                pass
            #    raw_elmt = self.safe_get(bs, tag_attr)
            #    raw_data["infos"][tag_name] = self.get_safe_pattern(raw_elmt, self.patterns.get(tag_name), self.groups.get(tag_name))

        raw_title = self.safe_get(bs, self.patterns.title_tag)
        title = self.get_safe_pattern(raw_title, self.patterns.title, self.groups.title)
        raw_ean = self.safe_get(bs, self.patterns.ean)
        ean = self.get_safe_pattern(raw_ean, self.patterns.ean, self.groups.ean)
        self.ean = ean
        #       self.infos = infos
        title = self.safeGet(bs, self.site.titleTag)
        body = self.safeGet(bs, self.site.bodyTag)
        if title != "" and body != "":
            content = Content(url, title, body)
            content.print()



for k, v in info_site["tags"].items():
    print(k)
    tag = safe_get(tmp, info_site["tags"].get(k))
    print(tag)
    print(info_site["patterns"].get(k))
    print(
        get_safe_pattern(tag, info_site["patterns"].get(k), info_site["groups"].get(k))
    )


# dir(etree.HTML(str(tmp)).xpath('//p[@class="fpOtherOffer"]')[0])

# r = safe_get(tmp, "//*[contains(text(),'pr_ean')]")

# url.startswith("https://www.cdiscount.com")
# r
# re.search(info_site["patterns"].get("ean"), r).group(0)

# info_site[]
# crawler = Crawler(cdiscound)

crawler.get_page("https://www.cdiscount.com")

tmp = Driver()
"""
