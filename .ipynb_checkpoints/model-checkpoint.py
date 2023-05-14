import re
import random
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.chrome.options import Options
from utils.poppup import popupmsg
from utils.configs import get_config


class Driver:

    def __init__(self, port=2023, chromedriver_path=None):
        self.port = port
        self.chromedriver_path = chromedriver_path
        self.options = Options().add_experimental_option("debuggerAddress", f"//127.0.0.1:{self.port}")
        self.service = Service(executable_path=self.chromedriver_path)
        self.driver = webdriver.Chrome(service=self.service, options=self.options)
    

class Website:

    def __init__(self, name, url, target_pattern, absolute_url, title_tag, ean_tag, price_tag, seller_tag, captcha_tag, seller_listing_tag):
        self.name = name
        self.url = url
        self.target_pattern = target_pattern
        self.absolute_url = absolute_url
        self.title_tag = title_tag
        self.ean_tag = ean_tag
        self.price_tag = price_tag
        self.seller_tag = seller_tag
        self.captcha_tag = captcha_tag
        self.seller_listing_tag = seller_listing_tag


class Content:

    def __init__(self, timestemp, url, title, ean, infos: dict):
        self.timestemp = timestemp
        self.url = url
        self.title = title
        self.ean = ean
        self.infos = infos


# =====================

class Crawler:
    def __init__(self, site):
        self.site = site
        # TODO: save visited pages to cloud storage
        self.visited = set()

    def get_page(self, url):
        driver = Driver()
        try:
            driver.get(url)
        except Exception as e:
            msg = f"This exception: {e} was raise when we try to get the page: {url}"
            popupmsg(msg)
            return None
        return BeautifulSoup(driver.page_source, 'html.parser')

    def wait(delay_min, delay_max):
        random_delay = random.randint(delay_min, delay_max)
        print(f"We wait for {random_delay} 's before continue")
        time.sleep(random_delay)

    def safe_get(self, pageObj, selector):
        selectedElems = pageObj.select(selector)
        if selectedElems is not None and len(selectedElems) > 0:
            return '\n'.join([elem.get_text() for elem in selectedElems])
        return ''

    def check_captcha(self, pageObj):
        is_captchat_found = False 
        try:
            selected_elems = pageObj.select(self.site.captcha_tag)
            is_captchat_found = selected_elems is not None and len(selected_elems) > 0
        except:
            is_captchat_found = False
        return is_captchat_found

    def parse(self, url):
        bs = self.getPage(url)
        if bs is not None:
            title = self.safeGet(bs, self.site.titleTag)
            body = self.safeGet(bs, self.site.bodyTag)
            if title != '' and body != '':
                content = Content(url, title, body)
                content.print()

    def crawl(self):
        """
        Get pages from website home page
        """
        bs = self.getPage(self.site.url)
        targetPages = bs.findAll('a', href=re.compile(self.site.targetPattern))
        for targetPage in targetPages:
            targetPage = targetPage.attrs['href']
            if targetPage not in self.visited:
                self.visited.append(targetPage)
                if not self.site.absoluteUrl:
                    targetPage = '{}{}'.format(self.site.url, targetPage)
                self.parse(targetPage)



cdiscound = Website('Cdiscount', 'https://www.cdiscount.com', '^(/.*)', True, 'h1', 'div.fpProductDescription', 'div.fpPrice', 'div.fpSeller', 'div.white-square')

crawler = Crawler(cdiscound)

crawler.get_page("https://www.cdiscount.com")

tmp = Driver()
