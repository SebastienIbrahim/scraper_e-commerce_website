import queue
from model import Website, Crawler, get_info_site

info_site = get_info_site(site="cdiscount", device="desktop")

cdiscount = Website(
    name=info_site.get("name"),
    target_pattern=info_site.get("target_pattern"),
    absolute_url=info_site.get("absolute_url"),
    tags=info_site.get("tags"),
    patterns=info_site.get("patterns"),
    groups=info_site.get("groups"),
    tags_get_from_seller_listing=info_site.get("tags_get_from_seller_listing"),
    batch=info_site["batch"],
    home_page=info_site["home_page"],
    shop_link_pattern=info_site["shop_link_pattern"],
    product_sheet_link_pattern=info_site["product_sheet_link_pattern"],
)

shops_queue = queue.Queue()

Crawler(cdiscount).crawl(shops_queue)
