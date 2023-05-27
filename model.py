import random
import re
import time
from typing import List
from lxml import etree
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import bs4
from utils.configs import get_config
from utils.poppup import popupmsg

# path =  "/home/mtd/Bureau/Ressistance/Projets/e-com-scrape/chromedriver_linux64/chromedriver"
path = "/home/user/Téléchargements/chromedriver_linux64/chromedriver"


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
        url,
        target_pattern,
        absolute_url,
        tags,
        patterns,
        groups,
        tags_get_from_seller_listing,
    ):
        self.name = name
        self.url = url
        self.target_pattern = target_pattern
        self.absolute_url = absolute_url
        self.tags = tags
        self.patterns = patterns
        self.groups = groups
        self.tags_get_from_seller_listing = tags_get_from_seller_listing


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

    def get_page(self, url):
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
                captured_elem[group].strip()
                for captured_elem in re.findall(pattern, selected_tag)
            ]
        except IndexError:
            elems = re.findall(pattern, selected_tag)[group]
        if len(elems) < 2:
            return "".join(elems)
        return elems

    def check_captcha(self, page_obj):
        is_captchat_found = False
        try:
            selected_elems = self.safe_get(page_obj, self.website_info.captcha)
            is_captchat_found = selected_elems is not None and len(selected_elems) > 0
        # TODO: handle this exception explicitly
        except:
            is_captchat_found = False
        return is_captchat_found

    def parse_seller_listing_page(self, bs: bs4.BeautifulSoup) -> List[dict]:
        """_summary_

        Args:
            bs (str): _description_

        Returns:
            List[dict]: _description_
        """
        selected_elems = self.safe_get(
            bs, self.website_info.tags_get_from_seller_listing.get("commom_tag")
        )
        tag_from_listing_page_raw_data = {
            tag: self.get_safe_pattern(
                selected_elems,
                self.website_info.patterns.get(tag),
                self.website_info.groups.get(tag),
            )
            for tag in self.website_info.tags_get_from_seller_listing.get("names")
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

    def parse(self, url):
        bs = self.get_page(url)
        if bs is not None:
            return bs

    def crawl(self, url):
        """
        Get pages from website home page
        """
        bs = self.get_page(url)
        print(re.compile(self.website_info.target_pattern))
        targetPages = bs.findAll("a", href=re.compile(self.website_info.target_pattern))
        for targetPage in targetPages:
            targetPage = targetPage.attrs["href"]
            if targetPage not in self.visited:
                self.visited.append(targetPage)
                if not self.website_info.absoluteUrl:
                    targetPage = "{}{}".format(self.website_info.url, targetPage)
                # self.parse(targetPage)
