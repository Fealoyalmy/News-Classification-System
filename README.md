# News Classification System
### Graduation Project
这是一个用 BiLSTM-Attention 模型训练的新闻分类算法

新闻数据爬取使用selenium完成，文本数据的预处理采用TF-IDF进行关键词提取，训练模型使用 keras + tensorflow 搭建

代码包括从数据采集，数据集预处理，模型搭建，模型训练以及最终可视化交互的全流程

1. TextClassification: 用于完成模型训练，测试  
2. TextProcessing: 用于完成数据集预处理
3. web: 部分为Flask服务端，包含静态资源文件、服务端启动程序与前端代码  
4. Spider`: 为爬虫模块，用于实现新闻数据的爬取操作（仅支持腾讯新闻与今日头条）

运行`/web`下的`app.py`以启动服务端程序，随后在浏览器访问`localhost:5000`即可
