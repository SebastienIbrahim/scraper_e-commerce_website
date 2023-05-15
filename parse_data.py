%load_ext autoreload
%autoreload 2
import time
import re
from model import Website, Crawler, Driver, get_info_site
from lxml import etree
info_site = get_info_site(site="cdiscount", device="desktop")

cdiscount = Website(
    name=info_site.get("name"),
    url=info_site.get("url"),
    target_pattern=info_site.get("target_pattern"),
    absolute_url=info_site.get("absolute_url"),
    tags=info_site.get("tags"),
    patterns=info_site.get("patterns"),
    groups=info_site.get("groups"),
)

crawler = Crawler(cdiscount)
url = "https://www.cdiscount.com/electromenager/aspirateurs-nettoyeurs/karcher-vc6-our-family-aspirateur-balai-multifon/f-1101410-kar4054278834221.html?idOffre=1884935695#mpos=0|mp"

tmp = crawler.get_page(url)

tmp.find_all({"0"})
dom = etree.HTML(str(tmp))
dom.xpath(cdiscount.price_tag)
cdiscound = Website('Cdiscount', 'https://www.cdiscount.com', '^(/.*)', True, 'h1', 'div.fpProductDescription', 'div.fpPrice', 'div.fpSeller', 'div.white-square', "")


def safe_get(page_obj, selector):
    selected_elems = etree.HTML(str(page_obj)).xpath(selector)
    if selected_elems is not None and len(selected_elems) > 0:
        try:
            return "\n".join([elem.text for elem in selected_elems])
        except AttributeError:
            return "\n".join([elem for elem in selected_elems])
    return ""


def get_safe_pattern(selected_tag: str, pattern: str, group: int):
    pattern = pattern or "(.*)"
    group = group or 0
    return "".join([elemt for elemt in re.search(pattern, selected_tag).group(group)]).strip()

get_safe_pattern(r, pattern=None)
re.findall("(.*)", r)

def parse_seller_listing_page(self, url):
    # TODO: check if it is absolute url or not
    bs = self.get_page(url)
    if bs is not None:
        for tag_name, tag_attr in self.tags.items():
            raw_elmt = self.safe_get(bs, tag_attr)
            self.data[tag_name] = self.get_safe_pattern(raw_elmt, self.patterns.get(tag_name), self.groups.get(tag_name))
        self.data["timestamp"] = int(time.time())
        self.data["url"] = url

def parse(self, url):
    bs = self.get_page(url)
    raw_data = {"infos": {}}
    if bs is not None:
        for tag_name, tag_attr in self.website_info.tags.items():
            if tag_name in ["tile", "ean", "url"]:
                raw_elmt = self.safe_get(bs, tag_attr)
                raw_data[tag_name] = self.get_safe_pattern(raw_elmt, self.patterns.get(tag_name), self.groups.get(tag_name))
                raw_data["timestamp"] = int(time.time())
            else:
                raw_elmt = self.safe_get(bs, tag_attr)
                raw_data["infos"][tag_name] = self.get_safe_pattern(raw_elmt, self.patterns.get(tag_name), self.groups.get(tag_name))

        raw_title = self.safe_get(bs, self.patterns.title_tag)
        title = self.get_safe_pattern(raw_title, self.patterns.title, self.groups.title)
        raw_ean = self.safe_get(bs, self.patterns.ean)
        ean = self.get_safe_pattern(raw_ean, self.patterns.ean, self.groups.ean)
        self.ean = ean
        self.infos = infos
        title = self.safeGet(bs, self.site.titleTag)
        body = self.safeGet(bs, self.site.bodyTag)
        if title != '' and body != '':
            content = Content(url, title, body)
            content.print()

for k, v in info_site["tags"].items():
    print(k)
    tag = safe_get(tmp, info_site["tags"].get(k))
    print(tag)
    print( info_site["patterns"].get(k))
    print(get_safe_pattern(tag, info_site["patterns"].get(k), info_site["groups"].get(k)))

dir(etree.HTML(str(tmp)).xpath('//p[@class="fpOtherOffer"]')[0])

r = safe_get(tmp, "//*[contains(text(),'pr_ean')]")

url.startswith("https://www.cdiscount.com")
r
re.search(info_site["patterns"].get("ean"), r).group(0)

info_site[]
crawler = Crawler(cdiscound)

crawler.get_page("https://www.cdiscount.com")

tmp = Driver()