'''
本程序使用python+selenium爬取智联招聘网的职位信息
通过浏览器对象设置，读取cookies可以实现自动登录网页
通过设置随机延时，可以防止被网站封IP
'''

# 导入包
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs
import time, os, json
import random
import requests
import pandas as pd

# 浏览器初始化
def chromeInit():
    '''
    浏览器初始化
    :return: browser
    '''
    # 设置浏览器的数据存放路径，可以读取cookies，实现自动登录网页
    profile_dir = r"C:\Users\admin\AppData\Local\Google\Chrome\User Data - 1"   # 对应你的chrome的用户数据存放路径
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--user-data-dir="+os.path.abspath(profile_dir))

    browser = webdriver.Chrome(chrome_options=chrome_options)
    browser.maximize_window()   # 最大化
    return browser

# 获取全国城市名称
def get_city(browser):
    '''
    获取全国城市名称
    :param browser: 浏览器对象
    :return: city_list
    '''
    url = 'https://www.zhaopin.com'
    browser.get(url)

    city_list = []      # 城市列表
    footer = browser.find_element_by_id('footer')
    ul = footer.find_element_by_xpath('./div/ul')
    cities = ul.find_elements_by_tag_name('strong')
    for c in cities:
        city_list.append(c.text.replace('|', ''))

    return city_list

# 获取智联网站上对应的城市码
def get_city_code(city):
    '''
    获取智联网站上对应的城市码
    :param city: 城市
    :return: code
    '''
    # 请求头
    headers = {'User-Agent':
                   'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/87.0.4280.66 Safari/537.36'
               }
    url = 'https://fe-api.zhaopin.com/c/i/city-page/user-city?ipCity=%s' % city
    res = requests.get(url, headers)
    code = json.loads(res.text)['data']['code']

    return code

# 获取职位信息
def get_jobs(browser, city):
    '''
    获取职位信息
    :param browser: 浏览器对象
    :param city: 城市
    :return: df_jobDetails
    '''
    # try:
    #     element = WebDriverWait(chrome, 5).until(
    #         EC.presence_of_element_located((By.CLASS_NAME, 'joblist-box__iteminfo iteminfo'))
    #     )
    # except:
    #     pass

    df_jobs = pd.DataFrame(columns=['职位', '公司', '职位链接'])
    df_jobDetails = pd.DataFrame(columns=['城市', '职位', '公司', '薪酬', '职位描述'])
    jobList = browser.find_element_by_class_name('positionlist').find_elements_by_xpath('./div')
    for job in jobList[:-2]:
        jobInfo = job.find_element_by_xpath('./a')
        # 获取职位链接
        jobLink = jobInfo.get_property('href')
        lines = jobInfo.find_element_by_xpath('./div')
        # 获取职位名称
        name = lines.find_element_by_xpath('./div[1]').find_element_by_tag_name('span').get_property('title')
        # 获取公司名称
        company = lines.find_element_by_xpath('./div[2]').text
        # 存入dataframe
        df_jobs = df_jobs.append({'职位': name,
                                  '公司': company,
                                  '职位链接': jobLink},
                                 ignore_index=True)

    # 遍历获取职位描述和薪酬
    for job in df_jobs.values:
        try:
            browser.get(job[2])
            summary = browser.find_element_by_class_name('summary-plane__content')
            # 获取薪酬
            salary = summary.find_element_by_xpath('./div[2]/div[1]/span').text
            # 获取职位描述
            jd = browser.find_element_by_class_name('describtion__detail-content').text
            # 存入dataframe
            df_jobDetails = df_jobDetails.append({'城市': city,
                                                  '职位': job[0],
                                                  '公司': job[1],
                                                  '薪酬': salary,
                                                  '职位描述': jd},
                                                 ignore_index=True)
        except TimeoutError:
            browser.refresh()       # 网页加载超时时刷新网页
        time.sleep(random.uniform(1.2, 1.5))  # 设置随机时间延时

    return df_jobDetails

if __name__ == '__main__':

    # 创建浏览器对象并初始化
    chrome = chromeInit()
    kw = '会计'       # 职位关键字
    cities = get_city(chrome)   # 城市列表，获取全国城市，也可以自己构建
    df_jobs = pd.DataFrame(columns=['城市', '职位', '公司', '薪酬', '职位描述'])
    chrome.set_page_load_timeout(30)  # 设置超时时间

    print('开始采集数据……')

    for city in cities[:8]:	# 爬取前8页

        city_code = get_city_code(city)     # 获取城市代码
        print('开始爬取%s的职位数据：' % city)
        page_num = 6        # 要爬取的页数
        for i in range(1, page_num):
            # 拼接完整的url
            url = 'https://sou.zhaopin.com/?jl=%d&kw=%s&p=%d' % (int(city_code), kw, i)
            chrome.get(url)
            time.sleep(2)
            chrome.refresh()
            print('\t爬取第%d页数据……' %  i)

            try:
                df_jobs = df_jobs.append(get_jobs(chrome, city))

            except TimeoutError:
                chrome.refresh()    # 超时时刷新页面
            except:
                break

    print('数据采集结束！')
    df_jobs.to_excel('智联职位.xlsx', index=False)

    chrome.close()



