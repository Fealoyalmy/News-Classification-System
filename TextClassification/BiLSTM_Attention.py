# @PROJECT : GetNewsType.py
# -*-coding:utf-8 -*-
# @TIME : 2022/3/7 16:50
# @Author : 寒露
# @File : .py

import pandas as pd
import keras
from keras import backend as K
from keras.engine.base_layer import Layer
from keras.preprocessing import sequence
from keras.models import Model
from keras.layers import Input, Dense, Embedding, LSTM, Bidirectional


class AttentionLayer(Layer):
    K.clear_session()  # 结束当前的TF计算图，并新建一个，有效避免模型/层的混乱

    def __init__(self, attention_size=None, **kwargs):
        self.attention_size = attention_size
        self.time_steps = None
        self.W = None
        self.b = None
        self.V = None
        super(AttentionLayer, self).__init__(**kwargs)

    def get_config(self):
        config = super().get_config()
        config['attention_size'] = self.attention_size
        return config

    # 定义权重
    def build(self, input_shape):
        assert len(input_shape) == 3  # 输入张量shape不为3则报异常

        self.time_steps = input_shape[1]
        hidden_size = input_shape[2]
        if self.attention_size is None:
            self.attention_size = hidden_size

        self.W = self.add_weight(name='att_weight', shape=(hidden_size, self.attention_size),
                                 initializer='uniform', trainable=True)
        self.b = self.add_weight(name='att_bias', shape=(self.attention_size,),
                                 initializer='uniform', trainable=True)
        self.V = self.add_weight(name='att_var', shape=(self.attention_size,),
                                 initializer='uniform', trainable=True)
        super(AttentionLayer, self).build(input_shape)

    # 编写层的功能逻辑。只需要关注传入call的第一个参数：输入张量
    def call(self, inputs):
        self.V = K.reshape(self.V, (-1, 1))  # 将张量的shape变换为指定shape
        H = K.tanh(K.dot(inputs, self.W) + self.b)  # 逐元素计算sigmoid值  dot求两个张量的乘积
        score = K.softmax(K.dot(H, self.V), axis=1)  # 返回张量的softmax值
        outputs = K.sum(score * inputs, axis=1)  # 在给定轴上计算张量中元素之和
        return outputs

    # 层更改了输入张量的形状，在这里定义形状变化的逻辑，让Keras能够自动推断各层的形状
    def compute_output_shape(self, input_shape):
        return input_shape[0], input_shape[2]


class BiLSTM_Attention:
    @staticmethod
    def create_classify_model(max_len, vocab_size, embedding_size, hidden_size, attention_size, class_nums):
        inputs = Input(shape=(max_len,), dtype='int32')
        x = Embedding(vocab_size, embedding_size)(inputs)
        x = Bidirectional(LSTM(hidden_size, dropout=0.2, return_sequences=True))(x)
        x = AttentionLayer(attention_size=attention_size)(x)
        outputs = Dense(class_nums, activation='softmax')(x)
        model = Model(inputs=inputs, outputs=outputs)
        model.summary()  # 输出模型结构和参数数量
        return model

    @staticmethod
    def train(data_list, label_list, vocab2idx, label2idx, train_r, val_r, history):
        """
        基于BiLSTM-Attention模型进行训练
        :param data_list: 数据集输入list
        :param label_list: 数据集输出list
        :param vocab2idx: 数据集输入索引表
        :param label2idx: 数据集输出索引表
        :param train_r: 训练集比例
        :param val_r: 验证集比例
        :param history: 训练曲线实例
        :return: 训练完成的模型
        """
        # 参数的初始化
        MAX_LEN = 100  # 10
        EMBEDDING_SIZE = 200  # 100
        HIDDEN_SIZE = 201  # 64
        ATT_SIZE = 50
        BATCH_SIZE = 64  # 64
        EPOCHS = 5  # t4 c9
        VOCAB_SIZE = len(vocab2idx)
        CLASS_NUMS = len(label2idx)
        count = len(label_list)  # 数据总量
        # 数据的填充，以及类别one-hot化
        new_datas = sequence.pad_sequences(data_list, maxlen=MAX_LEN)
        new_labels = keras.utils.np_utils.to_categorical(label_list, CLASS_NUMS)
        # 根据比例划分训练集、测试集、验证集
        x_train, y_train = new_datas[:int(count * train_r)], new_labels[:int(count * train_r)]
        x_val = new_datas[int(count * train_r) - 1: int(count * (train_r + val_r)) - 1]
        y_val = new_labels[int(count * train_r) - 1: int(count * (train_r + val_r)) - 1]
        x_test, y_test = new_datas[int(count * (train_r + val_r)) - 1:], new_labels[int(count * (train_r + val_r)) - 1:]

        # 根据参数创建模型
        md = BiLSTM_Attention.create_classify_model(MAX_LEN, VOCAB_SIZE, EMBEDDING_SIZE, HIDDEN_SIZE, ATT_SIZE, CLASS_NUMS)
        # 选择损失函数和优化函数
        md.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        # 训练模型
        if val_r != 0:  # 存在验证集
            md.fit(x_train, y_train, batch_size=BATCH_SIZE, epochs=EPOCHS, validation_data=(x_val, y_val), verbose=2,
                   callbacks=[history])
            if train_r + val_r < 1:  # 存在测试集
                score, acc = md.evaluate(x_test, y_test, batch_size=BATCH_SIZE)  # 模型评估
                print('score:', score, 'accuracy:', acc)
        else:  # 数据集全训练
            md.fit(x_train, y_train, batch_size=BATCH_SIZE, epochs=EPOCHS, verbose=2, callbacks=[history])

        return md


"""
26万标题数据训练：
128 11 50 128  ep2  =82.99
128 11 50 64   ep2  =83.09
128 11 50 32   ep2  =83.59
128 27 50 64   ep2  =84.18  76.73
128 27 50 1024 ep2  =82.78  75.98
128 27 50 2048 ep2  =82.67  76.32 

7500新闻内容数据训练：
128 19 50 32   ep5  =       92.67
128 19 50 1    ep5  =93.00  93.87 


"""

