import fire
import os
import time
import json
import pathlib
import shutil

def new_spider():
    print("New Spider:")

    while True:
        try:
            nums = int(input("请输入爬取新闻页数(一页50条)："))
            assert nums > 0
            break
        except:
            print("输入数字不合法( n > 0 )!")
    print("新闻种类:")
    key_match = {
        "1": "全部",
        "2": "国内",
        "3": "国际",
        "4": "社会",
        "5": "体育",
        "6": "娱乐",
        "7": "军事",
        "8": "科技",
        "9": "财经",
        "10": "股市",
        "11": "美股",
        "12": "国内_国际",
        "13": "国内_社会",
        "14": "国际_社会",
        "15": "国内国际社会"
    }
    for i in key_match:
        print("\t"+i+". "+key_match[i])
    while True:
        try:
            n = int(input("请输入要爬取新闻种类:"))
            assert n>0 and n<16
            break
        except:
            print("输入数字不合法( 1<=n<=15 )!")

    task_id = str(int(time.time()))
    if not os.path.exists("save"):
        os.mkdir("save")
    os.mkdir("save/"+task_id)
    with open("save/"+task_id+"/app.dump", "w", encoding="utf-8") as f:
        f.write(json.dumps({"task_id":task_id, "range":nums, "lid":key_match[str(n)], "finished": 0}, ensure_ascii=False))
    with open("app.dump", "w", encoding="utf-8") as f:
        f.write(json.dumps({"task_id":task_id, "range":nums, "lid":key_match[str(n)], "finished": 0}, ensure_ascii=False))
    print("爬虫即将开始，此次任务ID为:", task_id)
    try:
        os.system("scrapy crawl get_news -s JOBDIR=save/"+task_id)
    except:
        pass
    print("任务结束")


def continue_task(task_id):
    if not pathlib.Path(os.getcwd()+"\\save\\"+str(task_id)+"\\spider.state").exists():
        print("任务ID不存在")
        return
    shutil.copy(os.getcwd()+"\\save\\"+str(task_id)+"\\app.dump", "app.dump")
    print("爬虫即将开始，此次任务ID为:", task_id)
    try:
        os.system("scrapy crawl get_news -s JOBDIR=save/" + str(task_id))
    except:
        pass
    print("任务结束")


def init_config():
    with open("config.json","w",encoding="utf-8") as f:
        f.write(json.dumps({"mysql_uri":"mysql+pymysql://root:password@127.0.0.1/database","mysql_table":"test"}, indent=4, ensure_ascii=False))
    print("已生成配置文件: config.json")

if __name__ == "__main__":
    fire.Fire({
        "new":new_spider,
        "continue":continue_task,
        "init_config": init_config
    })

