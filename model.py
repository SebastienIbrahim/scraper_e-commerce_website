#!/usr/bin/env python
# coding: utf-8

# In[60]:


import os
import random
import re
import time
import selenium
import yaml
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from utils.configs import get_config
from utils.poppup import popupmsg

get_ipython().run_line_magic('load_ext', 'jupyter_black')
get_ipython().run_line_magic('load_ext', 'pycodestyle_magic')


# In[59]:


x = lambda x: x.__version__
x(yaml)


# In[16]:


path = "/home/user/Téléchargements/chromedriver_linux64/chromedriver"


# In[17]:


os.getcwd()
print(os.path.abspath(os.curdir))
owd = os.getcwd()
os.chdir("..")
print(os.path.abspath(os.curdir) + "")
os.chdir("..")
print(os.path.abspath(os.curdir))
os.chdir(owd)
os.getcwd()


# In[ ]:


usr/bin/google-chrome(--remote-debugging-port=2023, --user-data-dir="/home/user/Téléchargements/chromedriver_linux64")


# In[22]:


class Driver:
    def __init__(self, port=2023, chromedriver_path=path):
        self.port = port
        self.chromedriver_path = chromedriver_path
        self.options = Options().add_experimental_option(
            "debuggerAddress", f"//127.0.0.1:{self.port}"
        )
        self.service = Service(executable_path=self.chromedriver_path)
        self.driver = webdriver.Chrome(service=self.service, options=self.options)


# In[24]:


class Website:
    def __init__(
        self,
        name,
        url,
        target_pattern,
        absolute_url,
        title_tag,
        ean_tag,
        price_tag,
        seller_tag,
        captcha_tag,
        seller_listing_tag,
    ):
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


# In[25]:


class Content:
    def __init__(self, timestemp, url, title, ean, infos: dict):
        self.timestemp = timestemp
        self.url = url
        self.title = title
        self.ean = ean
        self.infos = infos


# =====================

# In[26]:


def get_info_site(site="cdiscount"):
    site = site
    for key, val in get_config()["sites"].items():
        print(key)
        if key == site:
            return val


info_site = get_info_site("leroymerlin")


# In[27]:


cdiscound = Website(
    name=info_site.get("name"),
    url=info_site.get("url"),
    target_pattern=info_site.get("target_pattern"),
    absolute_url=info_site.get("absolute_url"),
    title_tag=info_site.get("title_tag"),
    ean_tag=info_site.get("ean_tag"),
    price_tag=info_site.get("price_tag"),
    seller_tag=info_site.get("seller_tag"),
    captcha_tag=info_site.get("captcha_tag"),
    seller_listing_tag=info_site.get("seller_listing_tag"),
)


# In[28]:


# os.listdir(os.getcwd()+"/Téléchargements/chromedriver_linux64/LICENSE.chromedriver")


# In[29]:


chromedriver_path = (
    os.getcwd() + "/Téléchargements/chromedriver_linux64" + "/chromedriver.exe"
)


# In[30]:


class Crawler:
    def __init__(self, website_info):
        self.website_info = website_info
        # self.site = site
        # TODO: save visited pages to cloud storage
        self.visited = set()

    def get_page(self, url):
        driver = Driver()
        try:
            driver.driver.get(url)
        except Exception as e:
            msg = f"This exception: {e} was raise when we try to get the page: {url}"
            popupmsg(msg)
            return None
        return BeautifulSoup(driver.driver.page_source, "html.parser")

    def wait(delay_min, delay_max):
        random_delay = random.randint(delay_min, delay_max)
        print(f"We wait for {random_delay} 's before continue")
        time.sleep(random_delay)

    def safe_get(self, pageObj, selector):
        selectedElems = pageObj.select(selector)
        if selectedElems is not None and len(selectedElems) > 0:
            return "\n".join([elem.get_text() for elem in selectedElems])
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

    def _beside():
        title = self.safe_get(bs, self.website_info.title_tag)
        body = self.safe_get(bs, self.website_info.body_tag)
        if title != "" and body != "":
            content = Content(url, title, body)
            content.print()

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

os.getcwd()
print(os.path.abspath(os.curdir))
owd = os.getcwd()
os.chdir("..")
print(os.path.abspath(os.curdir))
os.chdir(owd)
os.getcwd()
# In[31]:


crawler = Crawler(cdiscound)
_bs = crawler.parse(
    "https://www.cdiscount.com/informatique/ordinateurs-pc-portables/apple-14-macbook-pro-2023-puce-apple-m2-pro/f-107096402-mphe3fna.html#mpos=0|cd"
)


# In[46]:


_bs.find_all("h1", {"itemprop": "name"})[0].text


# In[17]:


def safe_get(pageObj, selector):
    selectedElems = pageObj.select(selector=selector)
    if selectedElems is not None and len(selectedElems) > 0:
        return "\n".join([elem.get_text() for elem in selectedElems])
    return ""


# In[33]:


with open("output1.html", "w") as file:
    file.write(str(_bs))


# In[26]:


for i in _bs.find_all("h1"):
    print(i, "\n")


# In[20]:


crawler.website_info.title_tag


# In[41]:


title = safe_get(_bs, crawler.website_info.title_tag)
#body = self.safe_get(bs, self.website_info.body_tag)


# In[ ]:




