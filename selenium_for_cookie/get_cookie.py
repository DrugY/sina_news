from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import os


USER = "**************"
PASS = "********************"



chrome_options = Options()
chrome_options.add_argument('--headless')
b = webdriver.Chrome(options=chrome_options)
b.get("https://login.sina.com.cn/signup/signin.php")
WebDriverWait(b,20).until(EC.element_to_be_clickable((By.CLASS_NAME, "W_btn_a")))
b.find_element_by_id("username").send_keys(USER)
b.find_element_by_id("password").send_keys(PASS)
b.find_element_by_class_name("W_btn_a").click()
time.sleep(5)
if b.current_url == "http://my.sina.com.cn/":
    print("登录成功")
    print(b.get_cookies())
else:
    print("登录失败")
b.quit()
os.system("pause")
