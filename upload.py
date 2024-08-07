# -*- coding: utf-8 -*-
from common import *
from split import *
import pyautogui
import autoit
from selenium.webdriver.common.keys import Keys
from DrissionPage import ChromiumPage, ChromiumOptions


class QQZonePictures:
    def __init__(self, driver, upload_path="./QQZone/", threads_num=4):
        self.driver = driver
        self.upload_path = upload_path
        self.threads_num = threads_num

    def autoit_select_files(self, dir_path, file_lists):
        autoit.win_wait("[TITLE:打开; CLASS:#32770; INSTANCE:1]", 5)
        autoit.win_activate("[TITLE:打开; INSTANCE:1]")
        time.sleep(1)
        print('输入路径')
        autoit.control_focus("打开", "[CLASS:ToolbarWindow32; INSTANCE:3]")
        autoit.control_click("打开", "[Class:ToolbarWindow32; instance:3]", text="地址", x=278, y=22)
        autoit.send(r'{LSHIFT}')
        autoit.send(dir_path)
        autoit.send("{ENTER}")
        autoit.send("{ENTER}")
        time.sleep(1)
        print('输入文件')
        autoit.control_focus("打开", "[CLASS:Edit; INSTANCE:1]")
        file_lists_str = ''
        for i in file_lists:
            file_lists_str += f'"{i}" '
        autoit.control_set_text("打开", "[CLASS:Edit; INSTANCE:1]", file_lists_str)
        time.sleep(1)
        autoit.control_click("打开", "[CLASS:Button; INSTANCE:1]")


    def upload_bk(self, album_url, dir_path, file_lists=None):
        # 不指定就默认全选
        file_lists = file_lists or os.listdir(dir_path)

        upload_fail_lists = []
        self.driver.get(album_url)
        WebDriverWait(driver, 10, 0.5).until(EC.presence_of_element_located((By.ID, r'tphoto')))
        print('进入相册成功')
        print('切换到 tphoto iframe')
        self.driver.switch_to.frame('tphoto')
        self.driver.find_element(by=By.XPATH, value='//*[@id="js-module-container"]/div[1]/div[3]/div/div/div/a[2]').send_keys(Keys.ENTER)
        print('切换回原始iframe')
        self.driver.switch_to.default_content()
        WebDriverWait(driver, 10, 0.5).until(EC.presence_of_element_located((By.ID, r'photoUploadDialog')))
        print('切换到 photoUploadDialog iframe')
        self.driver.switch_to.frame('photoUploadDialog')
        print('选择照片和视频')
        self.driver.find_element(by=By.CLASS_NAME, value='btn-select-img').click()
        time.sleep(2)

        self.autoit_select_files(dir_path, file_lists)
        
        WebDriverWait(driver, 5, 0.5).until(EC.presence_of_element_located((By.ID, r'photo_type_1')))
        print('选择高清')
        self.driver.find_element(by=By.ID, value='photo_type_1').click()
        print('开始上传')
        self.driver.find_element(by=By.CLASS_NAME, value='j-btn-start').click()

        self.driver.switch_to.default_content()
        while True:
            try:
                soup = BeautifulSoup(driver.page_source, 'lxml')
                _ = soup.find_all('iframe', id='photoUploadDialog')[0]
                if soup.find('div', class_='ui-popup-show'):
                    self.driver.find_element(by=By.CLASS_NAME, value='qz-right').click()
                    time.sleep(1)
                    self.driver.switch_to.frame('photoUploadDialog')
                    items = self.driver.find_elements(by=By.CLASS_NAME, value='j-photolist-item-name')
                    fail_lists = [os.path.join(dir_path, item.get_property('value')) for item in items]
                    upload_fail_lists.extend(fail_lists)
                    print(f'本次有{len(items)}张图片上传失败...')
                    break
                    
                print('等待上传中...')
            except:
                break
            time.sleep(5)
        print('上传完成')
        return upload_fail_lists

    def upload(self, album_url, dir_path, file_lists=None):
        # 不指定就默认全选
        file_lists = file_lists or os.listdir(dir_path)

        upload_fail_lists = []
        self.driver.get(album_url)
        pyautogui.alert(title='自动登陆失败', text='请手动完成登录后，点击确认!', button='确认')
        
        try:
            self.driver.ele('.:j-album-new-upload-btn-inline', timeout=5).click()
        except:
            self.driver.ele('.:j-album-new-upload-btn').click()
        self.driver.ele('#photoUploadDialog')
        print('选择照片和视频')
        self.driver.ele('.btn-select-img').click()
        time.sleep(2)

        self.autoit_select_files(dir_path, file_lists)
        
        print('选择高清')
        self.driver.ele('#photo_type_1').click()
        print('开始上传')
        self.driver.ele('.:j-btn-start').click()
        self.driver.wait.load_start()
        while True:
            try:
                
                if len(self.driver.eles('.:photo_upload_complete')):
                    print('上传成功')
                    break
                elif len(self.driver.eles('.:j-btn-start')) and 'j-uploading-show' in self.driver.ele('.:j-btn-start').attr('class'):
                    self.driver.ele('.:j-btn-start').click()
                elif len(self.driver.eles('.:j-btn-cancel')) and 'j-uploading-show' in self.driver.ele('.:j-btn-cancel').attr('class'):
                    print('上传中...')
                elif len(self.driver.eles('#:ui-popup-show')):
                    items = self.driver.eles('.j-photolist-item-name')
                    fail_lists = [os.path.join(dir_path, item.attr('value')) for item in items]
                    upload_fail_lists.extend(fail_lists)
                    print(f'本次有{len(items)}张图片上传失败...')
                    print('继续上传...')
                    self.driver.ele('.ui-dl-ft').ele('.:qz-right').ele('.qz-button').click()
            except Exception as e:
                print(e)
                break
            time.sleep(1)
        print('上传完成')
        return upload_fail_lists



if __name__ == "__main__":
    '''
    将root_dir_path中的照片，按每个文件夹split_num张图进行拆分；
    然后将图片上传到username用户的album_url相册中。
    注意，QQ相册一次最多500张
    '''
    username = '1585336145'
    album_url = 'https://user.qzone.qq.com/1585336145/photo/V52uocEf4Lb6fO3wr1Rp2AZBeo0qBn7s'
    root_dir_path = r'C:\QQ空间相册下载\QQZone\abc'
    # 是否需要预先分割为500张图片为一个文件夹
    need_split = True
    split_num = 500

    print('>> 1.先模拟登陆获取cookie')
    zone = QQZone(username=username)
    try:
        # cookies, gtk, uin, driver = zone.login(close=False)
        # cookies = convert_cookie(cookies)
        co = ChromiumOptions().set_browser_path(zone.browser_path)
        driver = ChromiumPage(addr_or_opts=co)
    except Exception as e:
        print('\n\n遇到错误了：\n' + str(e))
        pyautogui.alert(title='遇到错误了', text=str(e), button='了解')
        # return
        exit()

    print('>> 2.再开始上传相册')   
    app = QQZonePictures(driver)
    if need_split:
        print('先拆分图片')
        dir_path_lists = split_files2(root_dir_path, split_num)
    else:
        dir_path_lists = [root_dir_path, ]
    
    try:
        upload_fail_lists = []
        for dir_path in dir_path_lists:
            print(f'当前上传目录为: {dir_path}')
            fail_lists = app.upload(album_url, dir_path)
            upload_fail_lists.extend(fail_lists)
    except Exception as e:
        pass
    finally:
        driver.quit()
    print('以下为上传失败的图片：')
    print('\n'.join(upload_fail_lists))






