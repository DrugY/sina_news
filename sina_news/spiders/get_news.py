# -*- coding: utf-8 -*-
import scrapy
import random
import json
import os
import time
from scrapy import Request
from sina_news.items import SinaNewsItem


def get_news_id(html):
    k1 = html.find("newsid: '")
    k2 = html.find("'", k1+9)
    return html[k1+9:k2]

def get_channel(html):
    #print(html)
    k1 = html.find("channel: '")
    k2 = html.find("'", k1+10)
    return html[k1+10:k2]


class GetNewsSpider(scrapy.Spider):
    name = 'get_news'
    allowed_domains = ['sina.com.cn']
    start_urls = []
    titleMap = {
         "全部": "2509",
         "国内": "2510",
         "国际": "2511",
         "社会": "2669",
         "体育": "2512",
         "娱乐": "2513",
         "军事": "2514",
         "科技": "2515",
         "财经": "2516",
         "股市": "2517",
         "美股": "2518",
         "国内_国际": "2968",
         "国内_社会": "2970",
         "国际_社会": "2972",
         "国内国际社会": "2974"
    }
    headers = {
        "Referer": "https://news.sina.com.cn/roll/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36"
    }
    def __init__(self):
        super().__init__()
        if os.path.exists("app.dump"):
            config = json.loads(open("app.dump", encoding="utf-8").read())
            self.range = config.get("range", 200)
            self.lid = self.titleMap[config.get("lid", "全部")]
            print("爬取页数: %d" % self.range)
            print("新闻类型: %s" % config.get("lid", "全部"))
        else:
            self.range = 200
            self.lid = "2509"
            print("爬取页数: %d" % self.range)
            print("新闻类型: %s" % "全部")
        print("总共预计约%d条新闻" % (50*self.range,))

    def start_requests(self):
        for page in range(1, self.range+1):
            item = SinaNewsItem()
            url = "https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=%s&k=&num=50&page=%d&r=%f" % (self.lid, page, random.random())
            item["url"] = url
            yield Request(url, headers=self.headers, callback=self.get_one_page_news)

    def get_one_page_news(self, response):
        resp = json.loads(response.body)
        if resp["result"]["status"]["code"] != 0:
            print("Error page code, skip :%s "% response.body)
            return None
        data = resp["result"]["data"]
        for new in data:
            item = SinaNewsItem()
            item["url"] = new["url"]
            item["time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(new["ctime"])))
            item["images"] = [ im["u"] for im in new["images"]]
            yield Request(new["url"], headers=self.headers, meta=item, callback=self.parse)


    def parse(self, response):
        try:
            meta = response.xpath("//meta[@name='mediaid']/@content")[0].extract()
        except:
            return None
        item = response.meta
        item["type"] = meta
        if meta == "创事记" or len(response.xpath("//h1[@class='main-title']/text()")) == 0:
            item["title"], item["subtitle"], item["article"] = self.csj_parser(response)
        else:
            item["title"], item["subtitle"], item["article"] = self.default_parser(response)
        channel = get_channel(response.body.decode())
        news_id = get_news_id(response.body.decode())
        return Request("http://comment5.news.sina.com.cn/page/info?format=json&channel=%s&newsid=%s" % (channel, news_id), headers=self.headers, meta={"item":item, "channel":channel, "news_id":news_id, "retry": 0}, callback=self.get_comment)

    def get_comment(self, response):
        resp = json.loads(response.body)
        meta = response.meta
        meta["retry"] +=1
        if resp["result"]["status"]["code"] != 0:
            if meta["retry"] < 3:
                # print("Error comment code, retry :%d " % meta["retry"])
                return Request("http://comment5.news.sina.com.cn/page/info?format=json&channel=%s&newsid=%s" % (response.meta["channel"], response.meta["news_id"]), headers=self.headers, meta=meta, callback=self.get_comment)
            else:
                print("Error comment code, skip")
                return None
        comments = resp["result"]["cmntlist"]
        item = response.meta["item"]
        item["comments"] = []
        for comment in comments:
            item["comments"].append({"user": comment["nick"], "content": comment["content"]})
        return item

    def csj_parser(self, response):
        title = response.xpath("//h1[@id='artibodyTitle']/text()")[0].extract()
        subtitle = ""
        article = "\n".join([p.xpath("string(.)")[0].extract() for p in response.xpath("//div[@id='artibody']//p")]).replace("\u3000","").strip()
        return title, subtitle, article

    def default_parser(self, response):
        title = response.xpath("//h1[@class='main-title']/text()")[0].extract()
        subtitle = response.xpath("//div[@class='second-title']/text()")[0].extract()
        article = "\n".join([p.xpath("string(.)")[0].extract() for p in response.xpath("//div[@class='article']//p")]).replace("\u3000","").strip()
        return title, subtitle, article

