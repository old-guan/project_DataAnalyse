'''
爬取网易云热榜歌单及歌单中前10歌曲的信息和评论
'''

# 导入包
import requests
import time
import re
import pandas as pd
import pymysql
import json
from bs4 import BeautifulSoup as bs

# 获取网页源码
def get_soup(url):
    '''
    获取网页源码
    :param url:目标链接
    :return:网页响应
    '''
    # 请求头
    headers = {'User-Agent':
                   'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/87.0.4280.66 Safari/537.36'
               }
    # 发起请求
    res = requests.get(url, headers=headers)    # 获取响应
    soup = bs(res.text, 'html.parser')
    return soup

# 获取歌单列表
def get_gedanList(url):
    '''
    爬取网易云音乐歌单列表中的歌单名及链接
    :param url: 目标链接
    :return: 无
    '''
    global main_url, cursor, db     # 声明全局变量
    global count_gedan

    # df_gedan = pd.DataFrame(columns=['歌单名', '歌单链接'])    # 定义存放歌单信息的DataFrame
    soup = get_soup(url)       # 获取网页内容
    listBox = soup.find('div', class_='g-bd')       # 定位元素
    ul_gedan = listBox.find('ul', class_='m-cvrlst f-cb')   # 定位到存放歌单列表的ul
    lst_li = ul_gedan.find_all('li')       # 获取所有的存放歌单信息的li
    for li in lst_li:   # 遍历，获取每个歌单的信息，并存入DataFrame
        p = li.find('p', class_='dec')      # 定位到p标签
        name = p.a.text     # 获取歌单名
        link = main_url + p.a.get('href')    # 获取歌单链接，并拼接完整
        id_gedan = link[link.index('=')+1:]     # 获取歌单id

        # 将歌单名及链接添加到DataFrame
        # df_gedan = df_gedan.append({'id': id_gedan,
        #                             '歌单名': name,
        #                             '歌单链接': link},
        #                            ignore_index=True)
        # 查询歌单是否在数据库中存在
        # 编写sql语句，查询歌单id是否在数据库中
        sql_query = "select count(1) from gedan where id = \'%s\'; " % id_gedan
        cursor.execute(sql_query)   # 执行语句
        result = cursor.fetchone()[0]  # 获取查询结果
        if result == 0:     # 如果不存在，则调用方法，获取歌单信息
            print('开始爬取第%d个歌单：%s……' % (count_gedan+1, name))
            get_gedanInfo(link)
            count_gedan += 1
            print('歌单：%s爬取完成！' % name)
        else:
            print('歌单：%s已爬取！' % name)

    # return df_gedan

# 获取歌单的信息及歌曲列表
def get_gedanInfo(url):
    '''
    获取歌单信息
    :param url:目标网址
    :return: 无
    '''
    global count_song

    id = url[url.index('=')+1:]     # 获取歌单id
    soup = get_soup(url)
    cntc = soup.find('div', class_='cntc')  # 定位元素

    # 获取歌单名
    title = cntc.find('div', class_='hd f-cb')\
                .find('div', class_='tit').h2.text

    # 获取歌单创建者
    creater = cntc.find('div', class_='user f-cb').span.a.text

    tags = ''   # 歌单标签
    a_tags = cntc.find('div', class_='tags f-cb').find_all('a')
    # 循环获取标签
    for a in a_tags:
        tags = tags + ' ' + a.text

    tb_song = soup.find('div', class_='n-songtb')   # 定位到歌曲列表
    num_songs = tb_song.find('span', id='playlist-track-count').text    # 获取歌曲数量
    # num_play = tb_song.find('strong', id='play-count').text      # 获取播放数

    # 编写sql，插入数据到gedan表
    sql_insert = "insert into gedan values('%s', '%s', '%s', '%s', '%s', '%s')" % \
                 (id, title, creater, tags, url, num_songs)
    try:
        cursor.execute(sql_insert)     # 执行sql语句
        db.commit()     # 提交事务
    except:             # 发生异常时回滚
        db.rollback()

    lis = tb_song.find('ul', class_='f-hide').find_all('li')
    # 遍历，获取歌曲信息
    for li in lis:
        a = li.find('a')
        link_song = main_url + a.get('href')       # 获取歌曲链接
        name_song = a.text     # 获取歌曲名称
        id_song = link_song[link_song.index('=')+1:]     # 获取歌歌曲id

        # 查询歌曲id和歌单id是否都存在数据库中，若否，则调用方法，获取歌曲信息
        sql_query = "select count(1) from song where id = \'%s\' and id_gedan = \'%s\';" % \
                    (id_song, id)
        cursor.execute(sql_query)
        result = cursor.fetchone()[0]
        if result == 0:
            sql_query = "select count(1) from song where id = \'%s\';" % id_song
            cursor.execute(sql_query)
            # 查询歌曲id是否在数据库中
            # 若无，则调用方法，爬取歌曲信息
            if cursor.fetchone()[0] == 0:
                print('\t开始爬取第%d首歌：%s的信息……' % (count_song+1, name_song))
                d_song = get_songInfo(link_song)
                count_song += 1
                print('\t歌曲：%s信息爬取完成！' % name_song)
                sql_insert = "insert into song values('%s', '%s', '%s', '%s')" % \
                             (id_song, name_song, id, d_song['singer'])
                try:
                    cursor.execute(sql_insert)
                    db.commit()
                except:
                    db.rollback()
            # 若有，则查询出歌手名称，然后插入记录到数据表
            else:
                sql_query = "select distinct singer from song where id = \'%s\';" % id_song
                cursor.execute(sql_query)
                singer = cursor.fetchone()[0]   # 查询出歌手名称
                sql_insert = "insert into song values('%s', '%s', '%s', '%s')" % \
                             (id_song, name_song, id, singer)
                try:
                    cursor.execute(sql_insert)
                    db.commit()
                except:
                    db.rollback()
        else:
            print('\t歌曲：%s已爬取。' % name_song)

# 获取歌曲信息
def get_songInfo(url):
    '''
    获取歌曲信息和评论
    :param url: 歌曲链接
    :return: 存放歌曲信息的字典
    '''

    id = url[url.index('=')+1:]     # 获取歌曲id
    dict_song = {}

    soup = get_soup(url)
    div_cnt = soup.find('div', class_='cnt')    # 定位元素
    name = div_cnt.find_all('div')[0].div.em.text       # 获取歌曲名称
    singer = div_cnt.find('p', class_='des s-fc4').span.text    # 获取歌手名称

    num = 30    # 要获取的评论数
    print('\t\t开始爬取歌曲评论……')
    get_musicCmt(id, num)     # 调用方法，获取歌曲评论
    print('\t\t歌曲评论爬虫完成！')

    # 将数据存入字典
    dict_song['id'] = id
    dict_song['name'] = name
    dict_song['singer'] = singer

    return dict_song

# 获取歌曲评论
def get_musicCmt(id_song, num):
    '''
    获取歌曲评论
    :param id_song: 歌曲id
    :param num: 要获取的最新评论数量
    :return: 无
    '''

    global count_cmt

    # 调用网易云api，获取歌曲评论
    url_api = 'http://music.163.com/api/v1/resource/comments/R_SO_4_%s?limit=%d' \
              % (id_song, num)
    count = 1
    response = get_soup(url_api)    # 网页响应
    try:
        result = json.loads(response.text)
    except:
        return 0

    # 将结果转换为字典格式
    dict_hotCmt = result['hotComments']     # 热门评论，只显示15条
    dict_cmt = result['comments']           # 一般评论
    for item in dict_hotCmt:
        id_hotCmt = item['commentId']
        hotCmt = item['content']
        sql = "insert into song_cmt values('%d', '%s', '%s', '%s')" %\
              (count, id_hotCmt, id_song, hotCmt)
        try:
            cursor.execute(sql)
            count += 1
            count_cmt += 1
            db.commit()
        except:
            db.rollback()

    for item in dict_cmt:
        id_cmt = item['commentId']      # 评论id
        comment = item['content'].replace('\n', '')       # 评论内容
        sql = "insert into song_cmt values('%d', '%s', '%s', '%s')" % \
              (count, id_cmt, id_song, comment)
        try:
            cursor.execute(sql)
            count += 1
            count_cmt += 1
            db.commit()
        except:
            db.rollback()


if __name__ == '__main__':
    main_url = 'https://music.163.com'      # 主网址
    url = 'https://music.163.com/discover/playlist/?order=hot&cat=全部&limit=35&offset='     # 歌单网址
    count_gedan = 0     # 歌单计数
    count_song = 0      # 歌曲计数
    count_cmt = 0       # 评论计数
    start_time = time.time()    # 开始时间

    # 打开MySQL数据库连接
    db = pymysql.connect('192.168.0.107', 'root', 'admin', 'HotMusic')
    cursor = db.cursor()        # 创建游标

    print('启动爬虫……')
    for i in range(5):      # 获取网易云歌单热榜前5页
        get_gedanList(url + str(i * 35))    # 调用函数，爬取歌单信息

    db.close()  # 关闭数据库连接

    end_time = time.time()  # 结束时间
    use_time = end_time - start_time    # 总耗时
    print('爬虫结束，共爬取歌单%d个、歌曲%d首、评论%d条，耗时：%.2f秒。' % \
          (count_gedan, count_song, count_cmt, use_time))
