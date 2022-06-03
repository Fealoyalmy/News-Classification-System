# @PROJECT : GetNewsType.py
# -*-coding:utf-8 -*-
# @TIME : 2022/3/16 19:14
# @Author : 寒露
# @File : .py

import jieba
import numpy as np
import pandas as pd
from tqdm import tqdm
from keras.models import load_model
from TextClassification.BiLSTM_Attention import AttentionLayer
from TextProcessing.Text_Preclean import Text_Preclean
from TextProcessing.Words_Utils import Words_Utils


def vocabs_process(test_data, maxlen, vocab2idx_path):
    """
    将原始待预测的文本处理为可输入模型的数据格式
    :param test_data: 单条待预测文本
    :param maxlen: 模型输入长度
    :param vocab2idx_path: 词库索引路径
    :return: 模型输入数据
    """
    np.set_printoptions(suppress=True)
    with open(vocab2idx_path, "r", encoding="utf8") as fo:
        vocab2idx = eval(fo.readline())
    stopwords = pd.read_csv("../TextProcessing/stop_words.txt", index_col=False, sep="\t", quoting=3, names=['stopword'],
                            encoding='utf-8')
    test_data = Words_Utils.line_drop_stpwd(test_data, stopwords, drop_num=True)
    # test_data = "".join(test_data)
    keyword = jieba.analyse.extract_tags("".join(test_data), topK=maxlen, withWeight=False)  # 取关键词
    print("测试关键词", keyword)
    test_index = [vocab2idx[word] if word in vocab2idx else vocab2idx['<UNK>'] for word in keyword]  # 获取对应索引值
    print("测试索引值", test_index)
    input_data = np.array([test_index[:maxlen] + [0] * (maxlen-len(test_index))])  # 转换为可以输入模型的数据
    return input_data


def batch_classify(test_path, max_len, model_path, vocab2idx_path, label2idx_path):
    """
    批量预测文件文本生成含有预测标签的Excel文件
    :param test_path: 待预测批文件路径
    :param max_len: 模型输入长度
    :param model_path: 模型路径
    :param label2idx_path: 标签索引路径
    :return:
    """
    df_test_index = Text_Preclean.test_data2df_index(test_path, vocab2idx_path, label2idx_path)
    # df_test_index = Text_Preclean.read_xlsx_index(test_path)
    with open(label2idx_path, "r", encoding="utf8") as fo:
        label2idx = eval(fo.readline())
    idx2label = {}
    for label, index in label2idx.items():
        idx2label[index] = label
    MAX_LEN = max_len  # 序列最大长度参数
    ATT_SIZE = 50  # attention中的参数
    # 加载模型
    model = load_model(model_path, custom_objects={'AttentionLayer': AttentionLayer(ATT_SIZE)}, compile=False)
    res_list = []
    np.set_printoptions(suppress=True)
    for test_index in tqdm(df_test_index.contents_index):
        input_data = np.array([test_index[:MAX_LEN] + [0] * (MAX_LEN - len(test_index))])  # 转换为可以输入模型的数据
        y_pred = model.predict(input_data)  # 预测结果
        result = {}  # index:预测结果 -> 类别:预测结果
        for idx, pred in enumerate(y_pred[0]):
            result[idx2label[idx]] = pred
        # 对预测类别按概率降序排序
        result_sorted = sorted(result.items(), key=lambda item: item[1], reverse=True)
        res_list.append(result_sorted[0][0])
    print(res_list)
    df_news = pd.read_excel(test_path, sheet_name=0, engine='openpyxl')
    df_test_res = pd.DataFrame({'pred_res': res_list, 'title': df_news.title, 'content': df_news.content})
    # df_test_res.to_excel("test_res.xlsx", index=False)
    return df_test_res

def prdict_one(test_data, max_len, model_path, label2idx_path, vocab2idx_path):
    """
    获取一条文本的预测结果
    :param test_data: 需预测的文本
    :param max_len: 模型输入长度
    :param model_path: 模型路径
    :param label2idx_path: 标签索引路径
    :param vocab2idx_path: 词库索引路径
    :return:
    """
    with open(label2idx_path, "r", encoding="utf8") as fo:  # 导出label索引
        label2idx = eval(fo.readline())
    idx2label = {}
    for label, index in label2idx.items():
        idx2label[index] = label
    MAX_LEN = max_len  # 序列最大长度参数
    ATT_SIZE = 50  # attention中的参数
    # 加载模型
    model = load_model(model_path, custom_objects={'AttentionLayer': AttentionLayer(ATT_SIZE)}, compile=False)
    input_data = vocabs_process(test_data, MAX_LEN, vocab2idx_path)  # 获取模型输入数据
    y_pred = model.predict(input_data)  # 预测结果
    result = {}  # index:预测结果 -> 类别:预测结果
    for idx, pred in enumerate(y_pred[0]):
        result[idx2label[idx]] = pred
    # 对预测类别按概率降序排序
    result_sorted = sorted(result.items(), key=lambda item: item[1], reverse=True)
    print(result_sorted)
    return result_sorted[0][0], result_sorted


if __name__ == "__main__":
    while True:
        test_data = input()
        # prdict_one(test_data, 10, "NewsTitleModel.h5",
        #            "../TextProcessing/title_dataset/label2idx.txt",
        #            "../TextProcessing/title_dataset/title_vocab2idx.txt")

        prdict_one(test_data, 100, "NewsContentModel_3.h5",
                   "../TextProcessing/content_dataset3/label2idx.txt",
                   "../TextProcessing/content_dataset3/vocab2idx.txt")

    # batch_classify("../TextProcessing/test_contents_index.xlsx", 100,
    #                "content_model=93.87.h5",
    #                "../TextProcessing/label2idx_2.txt")




