# @PROJECT : GetNewsType.py
# -*-coding:utf-8 -*-
# @TIME : 2022/3/16 19:15
# @Author : 寒露
# @File : .py

import pandas as pd
from tqdm import tqdm
from TextProcessing.Words_Utils import Words_Utils


class Text_Preclean:
    @staticmethod
    def read_xlsx_data(xlsx_path):
        """
        读原数据集xlsx文件
        :param xlsx_path: 原数据集xlsx文件路径
        :return: 原数据集DataFrame
        """
        # 读取原始数据集
        df_news = pd.read_excel(xlsx_path, sheet_name=0, engine='openpyxl')
        df_news = df_news.dropna()
        # 对应列值转列表
        content = df_news.content.values.tolist()  # 内容
        title = df_news.title.values.tolist()  # 标题
        label = df_news.label.values.tolist()  # 分类
        # 将分词后的列表导入为DataFrame对象
        df_news_list = pd.DataFrame(
            {'label': label, 'content': Words_Utils.cut_word(content), 'title': Words_Utils.cut_word(title)})  #
        return df_news_list

    @staticmethod
    def read_txt_data(txt_path):
        """
        读原数据集txt文件
        :param txt_path: 原数据集txt文件路径
        :return: 原数据集DataFrame
        """
        with open(txt_path, "r", encoding="utf8") as fo:
            all_lines = fo.readlines()  # 读所有行
        id_list = []
        label_list = []
        title_list = []
        content_list = []
        for line in tqdm(all_lines, desc="读取新闻文本文件"):  # 按每行新闻加载进度条
            news_id, label, title, content = line.strip().split("_|_")
            id_list.append(news_id)
            label_list.append(label)
            title_list.append(title)
            content_list.append(content)
        df_news_list = pd.DataFrame({'label': label_list, 'title': title_list, 'content': content_list})
        # print(df_news_list)
        return df_news_list

    @staticmethod
    def get_train_data(df_news_list):
        """
        处理停用词并得到标题与内容的关键词
        :param df_news_list: 新闻原DataFrame
        :return: 训练数据DataFrame
        """
        # 导入忽略词
        stopwords = pd.read_csv("../TextProcessing/stop_words.txt", index_col=False, sep="\t", quoting=3,
                                names=['stopword'], encoding='utf-8')
        # 转换列表类型
        contents = df_news_list.content.values.tolist()
        titles = df_news_list.title.values.tolist()
        stopwords = stopwords.stopword.values.tolist()
        # 去除忽略字符
        contents_clean = Words_Utils.drop_stopwords(contents, stopwords, drop_num=True)
        titles_clean = Words_Utils.drop_stopwords(titles, stopwords, drop_num=True)
        # print(contents_clean)
        content_keyword = Words_Utils.get_keyword(contents_clean, 100)  # , ifPrint=True
        title_keyword = Words_Utils.get_keyword(titles_clean, 10)
        train_data = pd.DataFrame({'label': df_news_list['label'], 'content_keyword': content_keyword,
                                   'title_keyword': title_keyword})
        return train_data

    @staticmethod
    def save_vocab(train_data, keyword, save_vocab_path):
        """
        将数据集中特定列的关键词写入特定词库
        :param train_data: 数据集DataFrame
        :param keyword: 需要存入词库的数据集中的列名
        :param save_vocab_path: 词库路径
        :return: 无
        """
        word_vocabs = []  # 数据集词典
        for cks in tqdm(train_data[keyword], desc="更新数据集词典"):
            for ck in cks:
                if ck not in word_vocabs:
                    word_vocabs.append(ck)
        with open(save_vocab_path, "w", encoding="utf8") as fw:
            for word in word_vocabs:
                fw.write(word + "\n")
        fw.close()
        print("词库更新完成！")

    @staticmethod
    def save_allvocabs(train_data, save_vocab_path):
        """
        将数据集中内容与标题的每个关键词写入词库
        :param train_data: 数据集DataFrame
        :param save_vocab_path: 词库路径
        :return: 无
        """
        word_vocabs = []  # 数据集词典
        for cks in tqdm(train_data.content_keyword, desc="更新全词库（正文）"):
            for ck in cks:
                if ck not in word_vocabs:
                    word_vocabs.append(ck)
        for cks in tqdm(train_data.title_keyword, desc="更新全词库（标题）"):
            for ck in cks:
                if ck not in word_vocabs:
                    word_vocabs.append(ck)
        with open(save_vocab_path, "w", encoding="utf8") as fw:
            for word in word_vocabs:
                fw.write(word + "\n")
        fw.close()
        print("全词库更新完成！")

    @staticmethod
    def keyword2idx(train_data, vocab2idx, label2idx):
        """
        根据输入的新闻原文文本与标签得到其对应的索引值list
        :param train_data: 训练数据集DataFrame
        :param vocab2idx: 新闻词-索引dict
        :param label2idx: 标签-索引dict
        :return: 返回新闻内容、标题与标签的索引值DataFrame
        """
        contents_index, titles_index, labels_index = [], [], []
        # 导出文本的id索引
        for content, title, label in zip(train_data['content_keyword'], train_data['title_keyword'], train_data['label']):
            index_content = [vocab2idx[word] if word in vocab2idx else vocab2idx['<UNK>'] for word in content]
            index_title = [vocab2idx[word] if word in vocab2idx else vocab2idx['<UNK>'] for word in title]
            index_label = label2idx[label]
            contents_index.append(index_content)
            titles_index.append(index_title)
            labels_index.append(index_label)
        # 构造索引list的DataFrame
        df_news_index = pd.DataFrame({'contents_index': contents_index, 'titles_index': titles_index,
                                      'labels_index': labels_index})
        return df_news_index

    @staticmethod
    def get_index(train_data, label_list, vocab_path, label2idx_path):
        """
        根据词库生成关键词对应的索引值，将索引值编表生产DataFrame
        :param train_data: 数据集DataFrame
        :param label_list: 标签组list
        :param vocab_path: 新闻词库路径->新闻词库索引路径
        :param label2idx_path: 标签路径->标签索引路径
        :return: 索引数据集DataFrame
        """
        # 获取内容与标签的索引dict
        vocab2idx, idx2vocab = Words_Utils.get_vocab_idx(vocab_path)
        label2idx, idx2label = Words_Utils.get_label_idx(label_list)
        # 将索引表写入文件
        with open(vocab_path, 'w', encoding='utf-8') as file:  # "content_vocab2idx.txt"
            file.write(str(vocab2idx))
        file.close()
        with open(label2idx_path, 'w', encoding='utf-8') as file:  # "label2idx.txt"
            file.write(str(label2idx))
        file.close()
        # 把处理过的标题文本和类别全部索引化，标题文本变成词编号序列，类别变成类别对应编号
        train_index = Text_Preclean.keyword2idx(train_data, vocab2idx, label2idx)
        return train_index


    @staticmethod
    def read_xlsx_index(xlsx_path):
        """
        读索引数据集xlsx文件
        :param xls_path: xlsx文件路径
        :return: 索引数据集DataFrame
        """
        # 读取Excel中的索引数据
        df_news_index = pd.read_excel(xlsx_path, sheet_name=0, engine='openpyxl')
        df_news_index = df_news_index.dropna()
        # print(df_news_index)
        # 对应列str值转数值list
        contents_index = [eval(ci) for ci in df_news_index.contents_index.values]  # 内容
        titles_index = [eval(ti) for ti in df_news_index.titles_index.values]  # 标题
        labels_index = df_news_index.labels_index.values.tolist()  # 分类标签
        # 将Excel中的原数据转换为数值list导入为DataFrame对象
        df_index_list = pd.DataFrame({'contents_index': contents_index, 'titles_index': titles_index,
                                     'labels_index': labels_index})
        return df_index_list

    @staticmethod
    def test_data2df_index(test_path, vocab2idx_path, label2idx_path):
        df_test = Text_Preclean.read_xlsx_data(test_path)
        test_data = Text_Preclean.get_train_data(df_test)
        # print(test_data)
        with open(vocab2idx_path, "r", encoding="utf8") as fo:
            vocab2idx = eval(fo.readline())
            fo.close()
        with open(label2idx_path, "r", encoding="utf8") as fo:
            label2idx = eval(fo.readline())
            fo.close()
        test_index = Text_Preclean.keyword2idx(test_data, vocab2idx, label2idx)
        # print(test_index)
        # test_index.to_excel("test_content_dataset/test_contents_index.xlsx", index=False)
        return test_index

    @staticmethod
    def train_data2df_index():
        train_data_path = "content_dataset/news_content_label_title.xlsx"  # 原始数据集路径
        df_news_list = Text_Preclean.read_xlsx_data(train_data_path)
        train_data = Text_Preclean.get_train_data(df_news_list)
        print(train_data)
        vocab2idx_path = "content_dataset3/vocab2idx.txt"
        Text_Preclean.save_allvocabs(train_data, vocab2idx_path)
        label2idx_path = "content_dataset3/label2idx.txt"  # 词库文件路径
        label_list = ["财经", "房产", "教育", "科技", "军事", "汽车", "体育", "游戏", "娱乐"]
        # label_list = ['游戏', '娱乐', '体育', '财经', '房产', '汽车', '教育', '科技', '军事', '旅游']
        train_index = Text_Preclean.get_index(train_data, label_list, vocab2idx_path, label2idx_path)
        print(train_index)
        train_index.to_excel("content_dataset3/train_contents_index.xlsx", index=False)


if __name__ == "__main__":
    Text_Preclean.test_data2df_index("../初赛测试集.xlsx", "../TextProcessing/content_dataset2/vocab2idx_2.txt",
               "../TextProcessing/content_dataset2/label2idx_2.txt")
    # Text_Preclean.train_data2df_index()


    # train_data_path = "title_dataset/train_title_index.xlsx"  # 原始数据集路径
    # df_news_list = df_news = pd.read_excel(train_data_path, sheet_name=0, engine='openpyxl')
    #
    # label_list = ['游戏', '娱乐', '体育', '财经', '房产', '汽车', '教育', '科技', '军事']  # 类别
    # idx2label = {idx: label for idx, label in enumerate(label_list)}
    #
    # new_labels = []
    # for idx in df_news_list.labels_index:
    #     new_labels.append(idx2label[idx])
    #
    # label_list = ["财经", "房产", "教育", "科技", "军事", "汽车", "体育", "游戏", "娱乐"]
    # label2idx, idx2label = Words_Utils.get_label_idx(label_list)
    #
    # new_idx = []
    # for label in new_labels:
    #     new_idx.append(label2idx[label])
    #
    # df_index_list = pd.DataFrame({'contents_index': df_news_list.contents_index, 'titles_index': df_news_list.titles_index,
    #                               'labels_index': new_idx})
    # df_index_list.to_excel("title_dataset/train_title_index2.xlsx", index=False)


