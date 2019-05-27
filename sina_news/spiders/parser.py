import requests
from lxml import etree


def get_news_id(html):
    k1 = html.find("newsid: '")
    k2 = html.find("'", k1+9)
    return html[k1+9:k2]

def get_channel(html):
    k1 = html.find("channel: '")
    k2 = html.find("'", k1+10)
    return html[k1+10:k2]


class NewsParser:
    headers = {
        "Referer": "https://news.sina.com.cn/roll/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36"
    }
    def __init__(self):
        self.meta_map = {
            "创事记": self.csj_spider
        }

    def parse_news(self, HTML, meta):
        if meta in self.meta_map.keys():
            return self.meta_map[meta](HTML)
        else:
            return self.default_spider(HTML)

    def csj_spider(self, HTML):
        title = HTML.xpath("//h1[@id='artibodyTitle']")[0].text
        subtitle = ""
        article = "\n".join([p.xpath("string(.)") for p in HTML.xpath("//div[@id='artibody']//p")]).strip()
        return title,subtitle,article

    def default_spider(self, HTML):
        title = HTML.xpath("//h1[@class='main-title']")[0].text
        subtitle = HTML.xpath("//div[@class='second-title']")[0].text
        article = "\n".join([p.xpath("string(.)") for p in HTML.xpath("//div[@class='article']//p")]).strip()
        return title, subtitle, article
