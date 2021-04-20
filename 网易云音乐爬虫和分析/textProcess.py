'''
文本处理：
中文分词、词频统计和绘制词云图
'''

from PIL import Image
from jieba import analyse, posseg  # 导入分析和词性标注模块
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import jieba
import collections
import wordcloud

# 中文分词
def cut_words(text):
    '''
    分词，去停用词。
    :param text: 需要分词的文本
    :return: cut_words
    '''
    print('开始分词……')
    file = r'stop_words.txt'    # 停用词文件路径
    stop_words = open(file, 'r', encoding='utf-8').readlines()   # 读取停用词文件内容
    lst_stop_words = [w.strip() for w in stop_words]  # 去除空格符
    # 停用词性：标点符号、连词、助词、副词、介词、时语素、的、数词、方位词、代词。
    stop_flags = ['x', 'c', 'u', 'd', 'p', 't', 'uj', 'm', 'f', 'r']

    cut_words = []      # 分词列表

    lst_kong = [' ', '\t', '\n', '\r', '']      # 空字符列表
    words = jieba.cut(text, HMM=True)       # 分词
    # 去掉停用词和单字
    for w in words:
        if len(w) > 1:
            if w not in lst_stop_words and w not in lst_kong:
                cut_words.append(w)
    print('分词结束！')
    return cut_words

# 词频统计
def word_count(words):
    '''
    统计词频
    :param words: 词语列表
    :return: df_word_count
    '''
    print('开始统计词频……')
    word_counts = collections.Counter(words)    # 词频统计
    df_word_count = pd.DataFrame()

    for k, v in word_counts.items():
        df_word_count = df_word_count.append({'word': k,
                                             '词频': v},
                                             ignore_index=True)
    print('词频统计结束！')
    return df_word_count

# 绘制词云图
def gen_word_cloud(words, imgFile, max):
    '''
    绘制词云图
    :param words: 词云列表
    :param imgFile: 词云图基图
    :param max: 生成图的词的最大数
    :return: None
    '''
    print('开始生成词云图……')
    # 导入图片
    image = Image.open(imgFile)
    MASK = np.array(image)
    # 创建词云对象
    WC = wordcloud.WordCloud(font_path='C:\\Windows\\Fonts\\SIMHEI.TTF',
                             max_words=max, mask=MASK, height=400,
                             width=400, background_color='white', repeat=False, mode='RGBA')   # 设置词云对象属性


    img = WC.generate(words)    # 生成词云图

    plt.imshow(img)
    plt.title('Gita')
    plt.axis('off')
    plt.savefig('./词云.jpg')
    # plt.show()
    print('词云图已生成并保存！')
