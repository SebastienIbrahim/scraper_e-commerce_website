import random
import re
import queue
from urllib.parse import urlparse
import time
from typing import List
from lxml import etree
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import bs4
import json
from utils.configs import get_config
from utils.poppup import popupmsg


path = "/home/mtd/Bureau/Ressistance/Projets/e-com-scrape/chromedriver_linux64/chromedriver"
# path = "/home/user/Téléchargements/chromedriver_linux64/chromedriver"


# /usr/bin/google-chrome --remote-debugging-port=2023 --user-data-dir="/home/mtd/Bureau/Ressistance/Bot/chromedriver_linux64"
class Driver:
    def __init__(self, port=2023, chromedriver_path=path):
        self.port = port
        self.chromedriver_path = chromedriver_path
        self.options = Options().add_experimental_option(
            "debuggerAddress", f"//127.0.0.1:{self.port}"
        )
        self.service = Service(executable_path=self.chromedriver_path)
        self.driver = webdriver.Chrome(service=self.service, options=self.options)


class Website:
    def __init__(
        self,
        name,
        target_pattern,
        absolute_url,
        tags,
        patterns,
        groups,
        tags_get_from_seller_listing,
        batch,
        home_page,
        shop_link_pattern,
        product_sheet_link_pattern,
    ):
        self.name = name
        self.target_pattern = target_pattern
        self.absolute_url = absolute_url
        self.tags = tags
        self.patterns = patterns
        self.groups = groups
        self.tags_get_from_seller_listing = tags_get_from_seller_listing
        self.batch = batch
        self.home_page = home_page
        self.shop_link_pattern = shop_link_pattern
        self.product_sheet_link_pattern = product_sheet_link_pattern


class Content:
    def __init__(self, timestemp, url, title, ean, infos: dict):
        self.timestemp = timestemp
        self.url = url
        self.title = title
        self.ean = ean
        self.infos = infos


def get_info_site(site: str = "cdiscount", device: str = "desktop"):
    return get_config(device)["sites"].get(site)


class Crawler:
    def __init__(self, website_info):
        self.website_info = website_info
        # self.site = site
        # TODO: save visited pages to cloud storage
        self.visited = set()
        self.driver = Driver()

    def get_page(self, url) -> bs4.BeautifulSoup:
        # driver = Driver()
        try:
            self.driver.driver.get(url)
        except Exception as e:
            msg = f"This exception: {e} was raise when we try to get the page: {url}"
            popupmsg(msg)
            return None
        bs = BeautifulSoup(self.driver.driver.page_source, "html.parser")
        if self.check_captcha(bs):
            msg = f"We have been blocked by the website: {self.website_info.name} because of captcha"
            popupmsg(msg)
        return bs

    def get_other_offers_page(self, other_offers_link: str) -> str:
        other_offers_link_normalized = self._normalize_url(other_offers_link)
        other_offers_page = self.get_page(other_offers_link_normalized)
        self.wait(3, 8)
        return other_offers_page

    def get_all_shops_urls(
        self,
        bs_other_offers_page: bs4.BeautifulSoup,
        shops_queue: queue.Queue,
        visited_shops_urls: set,
    ) -> List[str]:
        """_summary_

        Args:
            bs_other_offers_page (str): _description_

        Returns:
            List[str]: _description_
        """
        all_shops_urls = []
        try:
            all_shops_urls = [
                self._normalize_url(url.attrs["href"])
                for url in bs_other_offers_page.find_all(
                    "a", href=re.compile(self.website_info.shop_link_pattern)
                )
                if url.attrs["href"] is not None
            ]
        except Exception as e:
            popupmsg(f"Error in get_all_shops_urls: {e}")
        for shop in all_shops_urls:
            if shop not in visited_shops_urls:
                shops_queue.put(shop)

    def get_all_product_sheet_links(self, bs: bs4.BeautifulSoup) -> List[str]:
        """Get all from given bs object.

        Args:
            bs (str): _description_
        """
        product_sheet_links = [
            link.attrs["href"]
            for link in bs.find_all(
                "a", href=re.compile(self.website_info.product_sheet_link_pattern)
            )
            if link.attrs["href"] is not None
        ]
        return product_sheet_links

    def wait(self, delay_min, delay_max):
        random_delay = random.randint(delay_min, delay_max)
        print(f"We wait for {random_delay} 's before continue")
        time.sleep(random_delay)

    def safe_get(self, page_obj: bs4.BeautifulSoup, selector: str) -> str:
        selected_elems = etree.HTML(str(page_obj)).xpath(selector)
        if selected_elems is not None and len(selected_elems) > 0:
            try:
                return "\n".join([elem.text.strip() for elem in selected_elems])
            except Exception as e:
                return "\n".join([elem for elem in selected_elems])
        return ""

    def get_safe_pattern(
        self, selected_tag: str, pattern: str = "(.*)", group: int = 0
    ) -> str:
        """_summary_

        Args:
            selected_tag (str): _description_
            pattern (str, optional): _description_. Defaults to "(.*)".
            group (int, optional): _description_. Defaults to 0.

        Returns:
            str: _description_
        """
        pattern = pattern or "(.*)"
        group = group or 0
        try:
            elems = [
                captured_elem[group].strip() if group != "NA" else captured_elem.strip()
                for captured_elem in re.findall(pattern, selected_tag)
            ]
        except IndexError:
            elems = (
                re.findall(pattern, selected_tag)
                if group < 0
                else re.findall(pattern, selected_tag)[group]
            )
        if len(elems) < 2:
            return "".join(elems)
        return elems

    def check_captcha(self, page_obj):
        is_captchat_found = False
        try:
            selected_elems = self.safe_get(
                page_obj, self.website_info.tags.get("captcha")
            )
            is_captchat_found = selected_elems is not None and len(selected_elems) > 0
        # TODO: handle this exception explicitly
        except:
            is_captchat_found = False
        return is_captchat_found

    def parse_product_sheet_page(self, bs_product_sheet: str) -> dict:
        """_summary_

        Args:
            bs_product_sheet (str): _description_

        Returns:
            dict: _description_
        """
        product_infos = {}
        for tag_name, tag_attr in self.website_info.tags.items():
            raw_elmt = self.safe_get(bs_product_sheet, tag_attr)
            product_infos[tag_name] = self.get_safe_pattern(
                raw_elmt,
                self.website_info.patterns.get(tag_name),
                self.website_info.groups.get(tag_name),
            )
        return product_infos

    def parse_other_offers(self, bs: str) -> List[dict]:
        """_summary_

        Args:
            bs (str): _description_

        Returns:
            List[dict]: _description_
        """
        tag_from_listing_page_raw_data = {
            tag: self.get_safe_pattern(
                self.safe_get(
                    bs, self.website_info.tags_get_from_seller_listing.get(tag)
                ),
                self.website_info.patterns.get(tag),
                self.website_info.groups.get(tag),
            )
            for tag in self.website_info.tags_get_from_seller_listing
        }
        offers = [
            {
                tag: tag_from_listing_page_raw_data[tag][seller_iterator]
                for tag in tag_from_listing_page_raw_data.keys()
            }
            for seller_iterator in range(
                len(tag_from_listing_page_raw_data["seller_name"])
            )
        ]
        return offers

    def parse_other_offers(self, bs: bs4.BeautifulSoup) -> List[dict]:
        """_summary_

        Args:
            bs (str): _description_

        Returns:
            List[dict]: _description_
        """
        tag_from_listing_page_raw_data = {
            tag: self.get_safe_pattern(
                self.safe_get(bs, self.website_info.tags_get_from_seller_listing[tag]),
                self.website_info.patterns.get(tag),
                self.website_info.groups.get(tag),
            )
            for tag in self.website_info.tags_get_from_seller_listing
        }
        offers = [
            {
                tag: tag_from_listing_page_raw_data[tag][seller_iterator]
                for tag in tag_from_listing_page_raw_data.keys()
            }
            for seller_iterator in range(
                len(tag_from_listing_page_raw_data["seller_name"])
            )
        ]
        return offers

    def _normalize_url(self, url: str) -> str:
        home_page_url_parts = urlparse(self.website_info.home_page)
        if not urlparse(url).netloc:
            if not url.startswith("/"):
                url = "/" + url
            return (
                "{}://{}".format(home_page_url_parts.scheme, home_page_url_parts.netloc)
                + url
            )
        return url

    def crawl(self, visited_shops_urls: set, shops_queue: queue.Queue):
        raw_data = {}
        home_page = self.get_page(self.website_info.home_page)
        self.wait(3, 7)
        product_sheet_links = self.get_all_product_sheet_links(home_page)
        for product_sheet_link in product_sheet_links:
            product_page = self.get_page(product_sheet_link)
            self.wait(4, 8)
            other_offers_link = self.safe_get(
                product_page, self.website_info.tags.get("seller_listing")
            )
            if other_offers_link:
                other_offers_page = self.get_other_offers_page(other_offers_link)
                self.get_all_shops_urls(
                    other_offers_page, shops_queue, visited_shops_urls
                )
                while not shops_queue.empty():
                    shop_infos = {}
                    shop_link = shops_queue.get()
                    print(f"Seller page to preprocessing: {shop_link} ...")
                    if shop_link not in visited_shops_urls:
                        shop_page = self.get_page(shop_link)
                        self.wait(3, 8)
                        # Get top products from shop page 1
                        top_product_page_1_links = self.get_all_product_sheet_links(
                            shop_page
                        )
                        for i, product_link in enumerate(top_product_page_1_links):
                            product_page = self.get_page(product_link)
                            self.wait(4, 8)
                            self.get_all_shops_urls(
                                product_page, shops_queue, visited_shops_urls
                            )
                            product_infos = self.parse_product_sheet_page(product_page)
                            other_offers_link = self.safe_get(
                                product_page,
                                self.website_info.tags.get("seller_listing"),
                            )
                            if other_offers_link:
                                other_offers_page = self.get_other_offers_page(
                                    other_offers_link
                                )
                                self.get_all_shops_urls(
                                    other_offers_page, shops_queue, visited_shops_urls
                                )
                                other_offers = self.parse_other_offers(
                                    other_offers_page
                                )
                                product_infos["offers"] = other_offers
                            shop_infos[f"product_{i+1}"] = product_infos
                        visited_shops_urls.add(shop_link)
                    raw_data.update(shop_infos)
                    if len(raw_data) % self.website_info.batch == 0:
                        # TODO: tranform raw_data in json format to dataframe and save to parquet
                        json_object = json.dumps(raw_data, indent=3)
                        jsonFile = open("all_top_product_shop.json", "w")
                        jsonFile.write(json_object)
                        jsonFile.close()
                        df = pd.read_json("all_top_product_shop.json").to_parquet(
                            "try_to_parquet.parquet", engine="fastparquet"
                        )
                        del raw_data
                    else:
                        pass
