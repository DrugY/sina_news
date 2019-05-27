# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
import hashlib
import json
from loguru import logger
from warnings import filterwarnings
from urllib.parse import urlparse


def md5(string):
    return hashlib.md5(string.encode("utf8")).hexdigest()


filterwarnings("ignore", category=pymysql.Warning)


class SinaNewsPipeline(object):
    def open_spider(self, spider):
        with open("config.json", encoding="utf8") as f:
            config = json.loads(f.read())
        with open("app.dump", encoding="utf-8") as f:
            self.dump = json.loads(f.read())
        self.table_name = config["mysql_table"]
        mysql_config = urlparse(config["mysql_uri"])
        self.db = pymysql.connect(
            host=mysql_config.hostname,
            port=mysql_config.port,
            user=mysql_config.username,
            password=mysql_config.password,
            db=mysql_config.path[1:]
        )
        self.cursor = self.db.cursor()
        self.cursor.execute(
            "CREATE TABLE if not exists `%s` (`id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, `title` varchar(255) NOT NULL, `subtitle` varchar(255)NOT NULL, `type` varchar(50) NOT NULL, `time` datetime(0) NOT NULL, `article` text NOT NULL, `images` varchar(1023) NOT NULL, `comments` text NOT NULL, `hash` char(32)NOT NULL, PRIMARY KEY (`id`) USING BTREE, UNIQUE INDEX `hash`(`hash`) USING BTREE ) ENGINE = InnoDB;" %
            self.table_name)
        print("当前已爬取%d条新闻" % self.dump["finished"])

    def process_item(self, item, spider):
        sql = "INSERT IGNORE INTO %s(`title`,`subtitle`,`type`,`time`,`article`,`images`,`comments`,`hash`) VALUES('%s','%s','%s','%s','%s','%s','%s','%s');" % (self.table_name,
        pymysql.escape_string(item["title"]), pymysql.escape_string(item["subtitle"]), item["type"], item["time"],
        pymysql.escape_string(item["article"]), ",".join(item["images"]),
        pymysql.escape_string(json.dumps(item["comments"], ensure_ascii=False)), md5(item["title"] + item["time"]))
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except:
            logger.exception(sql)
            self.db.rollback()
        self.dump["finished"] += 1
        if self.dump["finished"] % 100 == 0:
            print("当前已爬取%d条新闻" % self.dump["finished"])
        return item

    def close_spider(self, spider):
        with open("save/"+self.dump["task_id"]+"/app.dump", "w", encoding="utf-8") as f:
            f.write(json.dumps(self.dump, ensure_ascii=False))
        self.cursor.close()
        self.db.close()
