import requests
import winreg  # 和注册表交互
import re
import zipfile
import os

requests.packages.urllib3.disable_warnings()


def getChromeVersion():
    try:
        # 从注册表中获得版本号
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r'Software\Google\Chrome\BLBeacon')
        version, type = winreg.QueryValueEx(key, 'version')
        version_re = re.compile(r'^[1-9]\d*\.\d*.\d*')  # 匹配前3位版本号的正则表达式

        print('Current Chrome Version: {}'.format(version))  # 这步打印会在命令行窗口显示
        return version
    except WindowsError as e:
        print('check Chrome failed:{}'.format(e))
        return ""

def install(paths):
    file_name = "chromedriver_win32.zip"
    download(file_name)
    zip_file = zipfile.ZipFile(file_name)
    for names in zip_file.namelist():
        for path in paths:
            print("[*] try to unzip file [%s] to path [%s]" % (file_name, path))
            zip_file.extract(names, path)
            print("[o] finish to unzip file [%s] to path [%s]" % (
        file_name, path))
    zip_file.close()
    os.remove(file_name)
    print("[!] finish to delete the temp file path [%s]" % file_name)
    print("[*] Start Check")
    try:
        check()
    except Exception as e:
        print("安装失败,错误信息{}".format(e))
        


def download(file_name):
    version = getChromeVersion()
    if version:
        url = 'https://chromedriver.storage.googleapis.com/{}/chromedriver_win32.zip'.format(version)
        header = {'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'zh-CN,zh;q=0.9',
                'cache-control': 'no-cache',
                'pragma': 'no-cache',
                'referer': 'https://chromedriver.storage.googleapis.com/index.html',
                'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
                'x-client-data': 'CIe2yQEIo7bJAQjBtskBCKmdygEI/I/LAQjr8ssBCJ75ywEI5oTMAQjzmswBCMqbzAEIm5zMAQ=='}
        try:
            response = requests.get(url, headers=header, verify=False, timeout=15)
            if response.status_code == 200:
                with open(file_name,"wb")as f:
                    f.write(response.content)
        except Exception as e:
            print(e)
    else:
        print("未查询到您的Chrome版本,请检查您的Chrome是否正确安装")

def check():
    try:
        from selenium import webdriver
    except:
        os.popen("pip install selenium")
        print("未安装selenium库,开始安装selenium库")
        from selenium import webdriver
    
    import time
    option = webdriver.ChromeOptions()
    option.add_experimental_option("excludeSwitches", ['enable-automation', 'enable-logging'])
    driver = webdriver.Chrome(options=option)
    driver.get('http://www.baidu.com')
    time.sleep(2)
    driver.close()
    driver.quit()

if __name__ == "__main__":
    paths = []
    path = input("请输入您的python安装目录,并确保其在环境变量中 >>")
    if path:
        paths.append(path.replace("\\","/"))
        print("您的安装目录为：{}".format(paths[0]))
        install(paths)
    else:
        print("输入错误")
    