# @PROJECT : GetNewsType.py
# -*-coding:utf-8 -*-
# @TIME : 2022/3/26 23:46
# @Author : 寒露
# @File : .py

import matplotlib.pyplot as plt
import keras
from keras import Sequential
from keras.datasets import mnist
from keras.layers import Dense, Activation, Dropout
from keras.optimizers import RMSprop
from keras.utils import np_utils


class LossHistory(keras.callbacks.Callback):
    def on_train_begin(self, logs={}):
        self.losses = {'batch': [], 'epoch': []}
        self.accuracy = {'batch': [], 'epoch': []}
        self.val_loss = {'batch': [], 'epoch': []}
        self.val_acc = {'batch': [], 'epoch': []}

    def on_batch_end(self, batch, logs={}):
        self.losses['batch'].append(logs.get('loss'))
        self.accuracy['batch'].append(logs.get('accuracy'))
        self.val_loss['batch'].append(logs.get('val_loss'))
        self.val_acc['batch'].append(logs.get('val_accuracy'))

    def on_epoch_end(self, batch, logs={}):
        self.losses['epoch'].append(logs.get('loss'))
        self.accuracy['epoch'].append(logs.get('accuracy'))
        self.val_loss['epoch'].append(logs.get('val_loss'))
        self.val_acc['epoch'].append(logs.get('val_accuracy'))

    def loss_plot(self, loss_type):
        iters = range(len(self.losses[loss_type]))  # 取x轴长度
        plt.figure()  # 创建一个图
        # plt.plot(x,y)，这个将数据画成曲线
        plt.plot(iters, self.accuracy[loss_type], 'r', label='train acc')
        plt.plot(iters, self.losses[loss_type], 'g', label='train loss')
        if loss_type == 'epoch':  # 如果训练不止一次全集循环则需绘制验证曲线
            plt.plot(iters, self.val_acc[loss_type], 'b', label='val acc')
            plt.plot(iters, self.val_loss[loss_type], 'k', label='val loss')
        plt.grid(True)  # 设置网格形式
        plt.xlabel(loss_type)  # 给x轴加注释
        plt.ylabel('acc-loss')  # 给y轴加注释
        plt.legend(loc="upper right")  # 设置图例显示位置
        plt.show()

    def acc_loss_plot(self, loss_type):
        iters = range(len(self.losses[loss_type]))  # 取x轴长度
        fig, ax1 = plt.subplots()
        ax1.plot(iters, self.accuracy[loss_type], 'r', label='train acc')
        ax2 = ax1.twinx()
        ax2.plot(iters, self.losses[loss_type], 'g', label='train loss')
        if loss_type == 'epoch':  # 如果训练不止一次全集循环则需绘制验证曲线
            ax1.plot(iters, self.val_acc[loss_type], 'b', label='val acc')
            ax2.plot(iters, self.val_loss[loss_type], 'k', label='val loss')
        ax1.set_xlabel(loss_type)
        ax1.set_ylabel('Accuracy')
        ax2.set_ylabel('Loss')
        ax1.legend(loc="upper left")  # 设置图例显示位置
        ax2.legend(loc="upper right")  # 设置图例显示位置
        plt.show()



if __name__ == "__main__":
    # 创建一个实例LossHistory
    history = LossHistory()
    # 变量初始化
    batch_size = 128
    nb_classes = 10
    nb_epoch = 10
    # 准备数据
    (X_train, y_train), (X_test, y_test) = mnist.load_data()
    X_train = X_train.reshape(60000, 784)
    X_test = X_test.reshape(10000, 784)
    X_train = X_train.astype('float32')
    X_test = X_test.astype('float32')
    X_train /= 255
    X_test /= 255
    print(X_train.shape[0], 'train samples')
    print(X_test.shape[0], 'test samples')
    Y_train = np_utils.to_categorical(y_train, nb_classes)
    Y_test = np_utils.to_categorical(y_test, nb_classes)

    # 建立模型
    model = Sequential()
    model.add(Dense(512, input_shape=(784,)))
    model.add(Activation('relu'))
    model.add(Dropout(0.2))
    model.add(Dense(512))
    model.add(Activation('relu'))
    model.add(Dropout(0.2))
    model.add(Dense(10))
    model.add(Activation('softmax'))

    # 编译训练、评估模型
    model.compile(loss='categorical_crossentropy',
                  optimizer=RMSprop(),
                  metrics=['accuracy'])
    model.fit(X_train, Y_train,
                batch_size=batch_size, nb_epoch=nb_epoch,
                verbose=1,
                validation_data=(X_test, Y_test),
                callbacks=[history])  # callbacks回调，将数据传给history

    # 模型评估
    score = model.evaluate(X_test, Y_test, verbose=0)
    print('Test score:', score[0])
    print('Test accuracy:', score[1])

    history.acc_loss_plot('epoch')
