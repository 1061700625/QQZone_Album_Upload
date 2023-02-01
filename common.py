from gui import Win, Simpledialog, SimpleMessagebox
from queue import Queue
import math
import threading
import time
from selenium.webdriver import ActionChains, ChromeOptions
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
import undetected_chromedriver as uc
from selenium.webdriver.support import expected_conditions as EC
import requests
import copy
from selenium.webdriver.common.by import By
import requests
import time
import json
import os
import pyautogui
from bs4 import BeautifulSoup
import win32api
import win32gui
from win32con import WM_INPUTLANGCHANGEREQUEST


class QQZone:
    def __init__(self, username=None, password=None, other_username=None):
        self.url_login = 'https://i.qq.com/'
        self.username = username
        self.password = password
        self.other_username = other_username
        self.qzonetoken = None
        self.cookies = None
        self.g_tk = None
        self.headers = {
            'host': 'user.qzone.qq.com',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.8',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:66.0) Gecko/20100101 Firefox/66.0',
            'connection': 'keep-alive',
            'referer': 'https://qzone.qq.com/',
        }
        # Chrome下载链接：http://xfxuezhang.cn/web/share/软件-电脑/Chrome.zip
        self.browser_path = r'Chrome/BitBrowser.exe'
        self.driver_path = r'Chrome/chromedriver.exe'

    def get_browser_options(self):
        options = Options()
        # self.options.add_argument("--blink-settings=imagesEnabled=false")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--disable-full-form-autofill-ios")
        options.add_argument("--disable-autofill-keyboard-accessory-view[8]")
        options.add_argument("--disable-single-click-autofill")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-blink-features")
        options.add_argument("--incognito")
        options.add_argument("--mute-audio")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-webgl")
        options.add_argument("--disable-javascript")
        options.add_argument("--lang=en_US")
        options.add_argument("--disable-client-side-phishing-detection")
        options.add_argument("--no-first-run")
        options.add_argument("--use-fake-device-for-media-stream")
        options.add_argument("--autoplay-policy=user-gesture-required")
        options.add_argument("--disable-features=ScriptStreaming")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-save-password-bubble")
        options.add_argument("--disable-background-networking")
        options.add_argument("--disable-domain-reliability")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.page_load_strategy = 'eager'
        return options

    def driver(self):
        chrome_options = self.get_browser_options()
        # 有头浏览器的写法
        driver = uc.Chrome(driver_executable_path=self.driver_path,
                           browser_executable_path=self.browser_path,
                           suppress_welcome=False,
                           options=chrome_options)
        driver.set_page_load_timeout(30)
        driver.set_script_timeout(30)
        driver.implicitly_wait(30)
        driver.get(self.url_login)

        if self.username and self.password:
            print('>> 提供了账号或密码，进入自动登录模式(不大建议)')
            print('>> 切换到登录表单')
            driver.switch_to.frame('login_frame')
            # 切换到账号密码登录
            log_method = driver.find_element(by=By.ID, value='switcher_plogin')
            log_method.click()
            # 输入账号密码，登录
            print('>> 输入账号中...')
            username = driver.find_element(by=By.ID, value='u')
            username.clear()
            username.send_keys(self.username)
            print('>> 输入密码中...')
            password = driver.find_element(by=By.ID, value='p')
            password.clear()
            password.send_keys(self.password)
            login_button = driver.find_element(by=By.ID, value='login_button')
            login_button.click()
            print('**此处若有滑块验证，请在10s内手动完成！！！**')
            print('**若未成功登录，请手动完成登录！！！**')
            time.sleep(10)
        else:
            print('>> 未提供账号或密码，进入手动登录模式')
        while True:
            try:
                # WebDriverWait(driver, 2, 0.5).until(
                    # EC.presence_of_element_located((By.ID, r'aIcenter')))
                _ = BeautifulSoup(driver.page_source, 'lxml').find_all('a', id='aIcenter')[0]
                print('>> 登陆成功!')
                break
            except:
                pyautogui.alert(title='自动登陆失败', text='请手动完成登录后，点击确认!', button='确认')
                print('>> 等待手动完成登录中, 可能较久，稍等一会儿...')
            time.sleep(1)
        driver.switch_to.default_content()

        # if self.other_username:
        #   print('>> 进入好友空间...')
        #   driver.get(r'https://user.qzone.qq.com/' + self.other_username)
        #   time.sleep(2)
        self.cookies = driver.get_cookies()
        return driver

    def back_session(self):
        # 创建一个session对象
        my_session = requests.session()
        headers = copy.deepcopy(self.headers)
        headers['host'] = 'h5.qzone.qq.com'
        # 将字典转为cookiejar, 这样就可以将cookie赋给session
        c = requests.utils.cookiejar_from_dict(
            self.cookies, cookiejar=None, overwrite=True)
        my_session.headers = headers
        # 将cookie赋给session
        my_session.cookies.update(c)
        return my_session

    # 生成g_tk
    def get_g_tk(self, driver):
        hashes = 5381
        for letter in driver.get_cookie('p_skey')['value']:
            hashes += (hashes << 5) + ord(letter)
        self.g_tk = hashes & 0x7fffffff
        return self.g_tk

    def login(self, close=True):
        print('>> 开始登陆')
        driver = self.driver()
        print('>> 获取g_tk')
        self.get_g_tk(driver)
        print('>> 登录完成')
        if close:
            driver.close()
            return self.cookies, self.g_tk, self.username
        return self.cookies, self.g_tk, self.username, driver


def convert_cookie(cookies):
    final_ck = ''
    for ck in cookies:
        final_ck += '{}={};'.format(ck['name'], ck['value'])
    return final_ck




def change_language(lang="EN"):
    """
    切换语言
    :param lang: EN––English; ZH––Chinese
    :return: bool
    """
    LANG = {
        "ZH": 0x0804,
        "EN": 0x0409
    }
    hwnd = win32gui.GetForegroundWindow()
    language = LANG[lang]
    result = win32api.SendMessage(
        hwnd,
        WM_INPUTLANGCHANGEREQUEST,
        0,
        language
    )
    if not result:
        return True

def set_english_inputer():
    # 0x0409为英文输入法的lid_hex的 中文一般为0x0804
    hwnd = win32gui.GetForegroundWindow()
    title = win32gui.GetWindowText(hwnd)
    im_list = win32api.GetKeyboardLayoutList()
    im_list = list(map(hex, im_list))
    result = win32api.SendMessage(hwnd, WM_INPUTLANGCHANGEREQUEST, 0, 0x0409)
    if result == 0:
        print("英文输入法切换成功！")