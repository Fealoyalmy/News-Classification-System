# @PROJECT : NewsClassificationSystem
# -*-coding:utf-8 -*-
# @TIME : 2022/4/10 18:22
# @Author : 寒露
# @File : .py
from urllib.parse import quote

import flask
import werkzeug
from flask import Flask, jsonify, request, Response, render_template, make_response, send_file
from flask_cors import CORS
import time
import json
import os
from werkzeug import secure_filename
from TextClassification import Classifier


app = Flask(__name__)
CORS(app)

app.config['JSON_AS_ASCII'] = False


def caculate_res(tres, cres):
    t_dic, c_dic = {}, {}
    for i in range(len(tres)):
        t_dic[tres[i][0]] = tres[i][1]
        c_dic[cres[i][0]] = cres[i][1]
    res = []
    for key, val in t_dic.items():
        res.append((key, t_dic[key] * 0.6 + c_dic[key] * 0.4))
    res.sort(key=lambda lab: lab[1], reverse=True)
    print(res)
    return res


@app.route('/', methods=['GET', 'POST'])
def ping_pong():
    return render_template('NewsClassify.html')  # （jsonify返回一个json格式的数据）


@app.route('/time', methods=['GET'])
def get_current_time():
    return jsonify({'time': time.time()})


@app.route('/getOne', methods=['GET', 'POST'])
def getone():
    if request.method == 'POST':
        input = request.get_json()
        label = '- -'
        title_list = [('--', '0.00'), ('--', '0.00'), ('--', '0.00'), ('--', '0.00'), ('--', '0.00')]
        content_list = [('--', '0.00'), ('--', '0.00'), ('--', '0.00'), ('--', '0.00'), ('--', '0.00')]
        print(input)

        if 'input_title' in input and input['input_title'] != '':
            # print(input['input_title'])
            tres_label, tres_list = Classifier.prdict_one(input['input_title'], 10,
                                                          "../TextClassification/NewsTitleModel.h5",
                                                          "../TextProcessing/title_dataset/label2idx.txt",
                                                          "../TextProcessing/title_dataset/title_vocab2idx.txt")
            for i in range(len(tres_list))[:5]:
                title_list[i] = (tres_list[i][0], str(round(tres_list[i][1] * 100, 2)))
            label = tres_list[0][0]
            # print(title_list)
        if 'input_content' in input and input['input_content'] != '':
            # print(input['input_content'])
            cres_label, cres_list = Classifier.prdict_one(input['input_content'], 100,
                                                          "../TextClassification/NewsContentModel.h5",
                                                          "../TextProcessing/content_dataset/label2idx.txt",
                                                          "../TextProcessing/content_dataset/vocab2idx.txt")
            for i in range(len(cres_list))[:5]:
                content_list[i] = (cres_list[i][0], str(round(cres_list[i][1] * 100, 2)))
            label = cres_list[0][0]
            # print(content_list)
        if 'input_title' in input and 'input_content' in input and \
                (input['input_title'] != '' or input['input_content'] != ''):
            res = caculate_res(tres_list, cres_list)
            label = res[0][0]

        data = {'label': label, 'title_res': title_list, 'content_res': content_list}  # 返回预测结果
        return data
    else:
        return render_template('NewsClassify.html')  # （jsonify返回一个json格式的数据）


@app.route('/getFile', methods=['GET', 'POST'])
def getfile():
    if request.method == 'POST':
        # file = request.files.get('filename')  # 获取文件 request.files.get('input_file', None)#
        file = request.files["filename"]
        # filename = secure_filename(file.filename)
        filename = file.filename  # 获取文件名
        print("上传文件：", filename)
        data = {
            'filename': 'predict_result.xlsx',
            'output': 'finished'
        }
        if filename != "":
            try:
                file.save(os.path.join('static/', filename))  # 'excel_test.xlsx'
                df_test_res = Classifier.batch_classify("../web/static/" + filename, 100,
                                                        "../TextClassification/NewsContentModel.h5",
                                                        "../TextProcessing/content_dataset/vocab2idx.txt",
                                                        "../TextProcessing/content_dataset/label2idx.txt")
                df_test_res.to_excel("static/predict_result.xlsx", index=False)
            except:
                data['output'] = '文件出错，请上传格式有效的xlsx或csv文件！'
        else:
            data['output'] = '无效的空文件!'
        return data
    else:
        return render_template('NewsClassify.html')  # （jsonify返回一个json格式的数据）


if __name__ == '__main__':
    # flask多线程导致使用Flask封装模型对外提供服务接口，调用时会发生错误，关闭多线程即可
    app.run(host='127.0.0.1', port=5000, threaded=False)


