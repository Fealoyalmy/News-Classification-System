# @PROJECT : GetNewsType.py
# -*-coding:utf-8 -*-
# @TIME : 2022/3/28 0:03
# @Author : 寒露
# @File : .py

import pandas as pd
import numpy as np
import keras
from keras.models import load_model
from keras.preprocessing import sequence
from TextClassification.BiLSTM_Attention import AttentionLayer, BiLSTM_Attention
from TextClassification import LossAcc_History
from TextProcessing.Text_Preclean import Text_Preclean, Words_Utils


def origine2train_data(data_path):
    df_news_list = Text_Preclean.read_txt_data(data_path)  # 读数据集源文件 "../DataSet/id_label_title.txt"
    train_data = Text_Preclean.get_train_data(df_news_list, 10)  # .iloc[0:100]取前100行
    print(train_data)
    train_data.to_excel("train_title.xlsx", index=False)  # 将预处理后的训练数据存excel
    Text_Preclean.save_vocab(train_data, 'title_keyword', "word_vocabs.txt")  # 保存更新词库文件


def train2index_data(train_data):
    if type(train_data) == 'str':
        train_data = pd.read_excel("train_title.xlsx", sheet_name=0, engine='openpyxl')  # 读预处理后的训练数据集
    train_index = Text_Preclean.get_index(train_data, "word_vocabs.txt")  # 根据词库文件构建索引数据集
    print(train_index)
    train_index.to_excel("train_index.xlsx", index=False)  # 符合模型输入格式的索引数据集存excel


def model_evaluate():  # 独立测试集评估新闻内容模型（测试集不准确）
    model_path = "content_model.h5"  # 模型的路径
    model = load_model(model_path, custom_objects={'AttentionLayer': AttentionLayer(50)}, compile=True)
    # model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    df_index = Text_Preclean.read_xlsx_index("../TextProcessing/test_content_dataset/test_contents_index_2.xlsx")
    df_index = df_index.reindex(np.random.permutation(df_index.index))  # 随机打乱DataFrame(防止测试集，验证集集中在某几个label上)
    data_list = df_index.contents_index
    label_list = df_index.labels_index
    x_test = sequence.pad_sequences(data_list, maxlen=100)
    y_test = keras.utils.np_utils.to_categorical(label_list, 9)
    score, acc = model.evaluate(x_test, y_test, batch_size=64)
    print('score:', score, 'accuracy:', acc)


def train_title():
    # 导入索引文件
    with open("../TextProcessing/title_dataset/title_vocab2idx.txt", "r", encoding="utf8") as fo:
        vocab2idx = eval(fo.readline())
        fo.close()
    with open("../TextProcessing/title_dataset/label2idx_2.txt", "r", encoding="utf8") as fo:
        label2idx = eval(fo.readline())
        fo.close()
    # 读取索引数据集文件转DataFrame
    df_index = Text_Preclean.read_xlsx_index("../TextProcessing/title_dataset/train_title_index2.xlsx")  # train_title_index.xlsx
    df_index = df_index.reindex(np.random.permutation(df_index.index))  # 随机打乱DataFrame(防止测试集，验证集集中在某几个label上)
    # 基于BiLSTM-Attention训练模型
    history = LossAcc_History.LossHistory()  # 实例化history绘制训练曲线
    ba_md = BiLSTM_Attention.train(df_index.titles_index, df_index.labels_index, vocab2idx, label2idx, 1, 0, history)
    # 保存训练好的模型
    ba_md.save("title_model.h5")
    print("模型保存成功！")
    history.acc_loss_plot('epoch')  # 绘制学习曲线


def train_content():
    # 导入索引文件
    with open("../TextProcessing/content_dataset/vocab2idx.txt", "r", encoding="utf8") as fo:
        vocab2idx = eval(fo.readline())
        fo.close()
    with open("../TextProcessing/content_dataset/label2idx.txt", "r", encoding="utf8") as fo:
        label2idx = eval(fo.readline())
        fo.close()
    # 读取索引数据集文件转DataFrame
    df_index = Text_Preclean.read_xlsx_index("../TextProcessing/content_dataset/train_contents_index.xlsx")
    df_index = df_index.reindex(np.random.permutation(df_index.index))  # 随机打乱DataFrame(防止测试集，验证集集中在某几个label上)
    # 基于BiLSTM-Attention训练模型
    history = LossAcc_History.LossHistory()  # 实例化history绘制训练曲线
    ba_md = BiLSTM_Attention.train(df_index.contents_index, df_index.labels_index, vocab2idx, label2idx, 1, 0, history)
    # 保存训练好的模型
    ba_md.save("NewsContentModel.h5")
    print("模型保存成功！")
    history.acc_loss_plot('epoch')  # 绘制学习曲线


if __name__ == "__main__":
    train_content()
    # train_title()

    # model_evaluate()




