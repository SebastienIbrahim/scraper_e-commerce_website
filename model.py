import random
import re
import time
from lxml import etree
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from utils.configs import get_config
from utils.poppup import popupmsg
get_config("desktop")

path = "/home/user/Téléchargements/chromedriver_linux64/chromedriver" #"/home/user/Téléchargements/chromedriver_linux64/chromedriver"

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
    ):
        self.name = name
        self.url = url
        self.target_pattern = target_pattern
        self.absolute_url = absolute_url
        self.tags = tags
        self.patterns = patterns
        self.groups = groups


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
        #driver = Driver()
        try:
            self.driver.driver.get(url)
        except Exception as e:
            msg = f"This exception: {e} was raise when we try to get the page: {url}"
            popupmsg(msg)
            return None
        return BeautifulSoup(self.driver.driver.page_source, "html.parser")

    def wait(delay_min, delay_max):
        random_delay = random.randint(delay_min, delay_max)
        print(f"We wait for {random_delay} 's before continue")
        time.sleep(random_delay)

    def safe_get(self, page_obj, selector):
        selected_elems = etree.HTML(str(page_obj)).xpath(selector)
        if selected_elems is not None and len(selected_elems) > 0:
            return "\n".join([elem.text for elem in selected_elems])
        return ""

    def check_captcha(self, pageObj):
        is_captchat_found = False
        try:
            selected_elems = pageObj.select(self.website_info.captcha_tag)
            is_captchat_found = selected_elems is not None and len(selected_elems) > 0
        except:
            is_captchat_found = False
        return is_captchat_found

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


def safe_get(pageObj, selector):
    selectedElems = pageObj.select(selector=selector)
    if selectedElems is not None and len(selectedElems) > 0:
        return "\n".join([elem.get_text() for elem in selectedElems])
    return ""




