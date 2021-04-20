'''
分析思路：
1、按歌单标签汇总，分析top10标签；
2、按歌手汇总，分析被收录top10歌手；
3、歌曲评论的词频统计和词云图。
'''

import pymysql
import pandas as pd
import time
import jieba
import wordcloud
from pyecharts.charts import Page, Bar, Pie
from pyecharts import options as opt
from textProcess import cut_words, word_count, gen_word_cloud

# 读取sql脚本
def readSqlScript(filename, path=''):
    '''
    读取sql脚本
    :param filename: 文件名
    :param path: 文件路径
    :return: sql
    '''
    # 读取脚本
    with open(path+filename, 'r', encoding='utf8') as f:
        lines = f.readlines()

    sql = ''.join(lines)    # 拼接成文本

    return sql

# 从数据库读取数据
def get_data(cursor, sql, columns) :
    '''
    从数据库读取数据
    :param cursor: 游标
    :param sql: sql语句
    :param columns: 字段名
    :return: df
    '''
    df = pd.DataFrame(columns=columns)
    len_col = len(df.columns)
    cursor.execute(sql)     # 执行语句
    result = cursor.fetchall()
    # 将数据存入df
    for data in result:
        d_tmp = {}
        for i in range(len_col):
            d_tmp[df.columns[i]] = data[i]
        df = df.append(d_tmp, ignore_index=True)

    return df

# 数据可视化
def plot_echart(df, type='Bar', title=None, theme='dark'):
    '''
    数据可视化
    :param df: 数据表
    :param type: 图像类型
    :param title: 图像标题
    :return: chart
    '''
    label_x = df.columns[0]
    x = list(df[label_x])
    label_y = df.columns[-1]
    y = list(df[label_y])
    chart = Bar()

    if type == 'Bar':   # 绘制柱形图
        chart = Bar(opt.InitOpts(theme=theme))
        x = list(df[label_x])       # x轴
        y = list(df[df.columns[-1]])    # y轴
        chart.add_xaxis(x)
        chart.add_yaxis(label_y, y)

    elif type == 'Pie':     # 绘制饼图
        x = df[label_x]
        chart = (
            Pie()
            .add(series_name=label_y, data_pair=list(zip(list(x), y)))
        )

    # 图像设置
    chart.set_global_opts(
        title_opts=opt.TitleOpts(title=title),
        toolbox_opts=opt.ToolboxOpts(is_show=True),
        legend_opts=opt.LegendOpts(pos_bottom=1)

    )

    return chart

if __name__ == '__main__':

    start_time = time.time()
    host = '192.168.0.107'      # 主机ip
    user = 'root'               # 用户名
    psw = 'admin'               # 密码
    db_name = 'HotMusic'        # 数据库名

    # 打开MySQL数据库连接
    db = pymysql.connect(host, user, psw, db_name)
    cursor = db.cursor()        # 创建游标

    print('开始从数据库获取数据……')
    file = ['analyse_歌手top10.sql',
            'analyse_歌单标签top10.sql']

    # 分析模型1：按歌单标签汇总，分析top10标签
    sql = readSqlScript(file[0])
    df_singerTop = get_data(cursor, sql, columns=['歌手', '被收录数'])

    # 分析模型2：按歌手汇总，分析被收录top10歌手
    sql = readSqlScript(file[1])
    df_gedanTop = get_data(cursor, sql, columns=['标签', '歌单数'])

    # 从数据库获取歌曲评论
    sql = 'SELECT t.song_cmt FROM song_cmt t ;'
    cursor.execute(sql)
    result = cursor.fetchall()
    comments = ''
    # 拼接成文本
    for r in result:
        comments = comments + r[0] + '\n'
    print('数据获取完毕！')
    cut_words = cut_words(comments)     # 分词
    print('前30个分词：\n', cut_words[:30])
    df_word_counts = word_count(cut_words)  # 统计词频
    # 词频排序
    df_word_counts = df_word_counts.sort_values(by='词频', ascending=False)[['word', '词频']]
    print('词频top30：\n', df_word_counts[:30])

    # 数据可视化
    page = Page(page_title='网抑云音乐歌曲爬取和分析')
    print('开始画图……')
    chart = plot_echart(df_singerTop, 'Pie', '歌手top10-饼图')
    page.add(chart)     # 添加到页面
    page.add(plot_echart(df_gedanTop, title='歌单标签top10-柱状图'))

    echart = plot_echart(df_word_counts[:15], type='Pie', title='歌曲评论词频统计-饼图')
    page.add(echart)

    echart = plot_echart(df_word_counts[:15], title='歌曲评论词频统计-柱状图', theme='romantic')
    page.add(echart)

    page.render()   # 输出到html文件

    img_file = 'gita.jpg'
    max_word = 100
    gen_word_cloud(' '.join(cut_words), img_file, max_word)
    print('画图结束！')
    end_time = time.time()

    print('耗时：%d秒。' % (end_time - start_time))
