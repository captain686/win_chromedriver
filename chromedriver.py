import difflib
import requests
import winreg  # 和注册表交互
import re
import zipfile
import os, re

requests.packages.urllib3.disable_warnings()


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

def getChromeVersion():
    try:
        # 从注册表中获得版本号
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r'Software\Google\Chrome\BLBeacon')
        version, type = winreg.QueryValueEx(key, 'version')
        print('Current Chrome Version: {}'.format(version))  # 这步打印会在命令行窗口显示
        return version
    except WindowsError as e:
        print('check Chrome failed:{}'.format(e))
        return ""

def install(paths):
    file_name = "chromedriver_win32.zip"
    version = getChromeVersion()
    download_status = download(file_name, version)
    if download_status:
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
    else:
        print("install fail")
        
def version_similar(version, prefixe):
    return difflib.SequenceMatcher(None, version, prefixe).quick_ratio()

def getPrefix(version:str):
    version_last = version.split(".")[-1]
    version_big = version.replace(f".{version_last}","")
    response = requests.get("https://chromedriver.storage.googleapis.com/?delimiter=/&prefix=")
    if response.status_code == 200:
        html = response.text
        prefixes = re.findall(f"<CommonPrefixes><Prefix>({version_big}.*?)/</Prefix></CommonPrefixes>",html)
        dif = 99
        for prefixe in prefixes:
            little = prefixe.split(".")[-1]
            new_dif = int(version_last) - int(little)
            if new_dif < dif:
                dif = new_dif
                version = version.replace(f"{version_last}", little)
        return version        
    else:
        return ""


def download(file_name, version):
    if version:
        print("开始下载")
        url = 'https://chromedriver.storage.googleapis.com/{}/chromedriver_win32.zip'.format(version)
        try:
            response = requests.get(url, headers=header, verify=False, timeout=15)
            if response.status_code == 200:
                with open(file_name,"wb")as f:
                    f.write(response.content)
                print("下载完成")
                return True
            elif response.status_code == 404:
                print("暂无此版本，尝试使用替代版本")
                prefix = getPrefix(version)
                if prefix:
                    download(file_name, prefix)
                    return True
                return ""
        except Exception as e:
            print(e)
            return False
    else:
        print("未查询到您的Chrome版本,请检查您的Chrome是否正确安装")
        return False

def check():
    try:
        from selenium import webdriver
    except:
        print("未安装selenium库,开始安装selenium库")
        os.system("pip install selenium")
        from selenium import webdriver
    
    import time
    option = webdriver.ChromeOptions()
    option.add_experimental_option("excludeSwitches", ['enable-automation', 'enable-logging'])
    driver = webdriver.Chrome(options=option)
    driver.get('https://ipinfo.io/')
    time.sleep(2)
    driver.close()
    driver.quit()

if __name__ == "__main__":
    paths = []
    path = input("请输入您的python安装目录,并确保其在环境变量中 >> ")
    if path:
        paths.append(path.replace("\\","/"))
        print("您的安装目录为：{}".format(paths[0]))
        install(paths)
    else:
        print("输入错误")
