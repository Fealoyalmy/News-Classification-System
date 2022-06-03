# @PROJECT : new1
# -*-coding:utf-8 -*-
# @TIME : 2021/7/13 14:17
# @Author : 寒露
# @File : .py

import jieba
import jieba.analyse
from tqdm import tqdm


class Words_Utils:
    @staticmethod
    def cut_word(sentence, size=None):
        """
        利用jieba分词
        :param sentence: 原句子
        :param size: 分词大小
        :return: 分好词的列表
        """
        content = []
        for line in sentence[:size]:
            current_segment = jieba.lcut(line)
            if len(current_segment) > 1 and current_segment != '\r\n':  # 换行符
                content.append(current_segment)
            else:
                content.append([])
        # print(content[1])  # (list of list)
        return content

    @staticmethod
    def line_drop_stpwd(line, stopwords, drop_num):
        line_clean = []
        num = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')
        for word in line:
            # 如果word的第一个字符为数字则去除该word
            if drop_num and word[0] in num:
                continue
            # 如果word在stopwords中则去除该word
            if word in stopwords or word == ' ':
                continue
            line_clean.append(word)
        return line_clean

    @staticmethod
    def drop_stopwords(contents, stopwords, drop_num=False):
        """
        去除需忽略的字符
        :param contents: 已分好词的句子
        :param stopwords: 需忽略的词
        :param drop_num: 是否去除数字（包括int与float)
        :return: 处理完成的句子列表
        """
        contents_clean = []
        # all_words = []
        for line in tqdm(contents, desc="去除停用词"):
            line_clean = Words_Utils.line_drop_stpwd(line, stopwords, drop_num)
            # all_words.append(str(word))
            contents_clean.append(line_clean)
        return contents_clean  # 处理后的内容、全部分词

    @staticmethod
    def get_keyword(contents, num, ifPrint=False):
        """
        基于TF-IDF模型批量处理list文本得到关键词
        :param contents: 文本list
        :param num: 输出关键词个数
        :param ifPrint: 是否打印关键字
        :return: 关键词list
        """
        i = 1
        keywords = []
        for cont in tqdm(contents, desc="筛选关键词"):
            contents_str = "".join(cont)
            res = jieba.analyse.extract_tags(contents_str, topK=num, withWeight=False)
            if ifPrint:
                print("第", i, "条内容关键词：")
                print(res, end="\n\n")
            keywords.append(res)
            i += 1
        return keywords

    @staticmethod
    def get_vocab_idx(save_vocab_path):
        """
        将数据集词库与特殊词拼接生成每个词的双向索引值dict
        :param save_vocab_path: 数据集词库路径
        :return: 词-索引，索引-词dict
        """
        special_words = ['<PAD>', '<UNK>']  # 特殊词
        with open(save_vocab_path, "r", encoding="utf8") as fo:
            word_vocabs = [word.strip() for word in fo]
        word_vocabs = special_words + word_vocabs
        idx2vocab = {idx: char for idx, char in enumerate(word_vocabs)}  # 索引-词
        vocab2idx = {char: idx for idx, char in idx2vocab.items()}  # 词-索引
        return vocab2idx, idx2vocab

    @staticmethod
    def get_label_idx(label_list):
        """
        获取标签的双向索引值dict
        :param label_list: 标签list
        :return: 标签-索引，索引-标签dict
        """
        label2idx = {label: idx for idx, label in enumerate(label_list)}  # 类别-索引
        idx2label = {idx: label for idx, label in enumerate(label_list)}  # 索引-类别
        return label2idx, idx2label

    @staticmethod
    def list2txt(path, words_list):
        """
        将词语列表转储为txt
        :param path: txt路径
        :param words_list: 词语列表
        :return: 无
        """
        # coding=utf-8
        with open(path, 'w', encoding='utf-8') as q:
            t = ''
            for e in words_list:
                t += e + '\r'
            q.write(t.strip(' '))

    @staticmethod
    def txt2list(path):
        """
        将txt导出为词语列表
        :param path: txt路径
        :return: 词语列表
        """
        file = open(path, 'r', encoding='utf-8')
        text = file.readlines()
        # print(text)
        words_list = []
        for t in text:
            t = t.replace("\n", "")
            words_list.append(t)
        return words_list




