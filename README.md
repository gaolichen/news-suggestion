# 基于NLP的新闻推荐浏览器插件

## 主要功能
- 基于浏览器的新闻浏览历史，用NLP技术生成新闻推荐条目。目前只根据chrome浏览器的历史，生成推荐条目。
- 用浏览器访问新闻站点时，高亮被推荐的新闻条目，效果如下图所示：

![exmple](/example.PNG)

## 运行环境
- 安装python运行环境的win10操作系统
- 支持油猴插件的浏览器，如chrome浏览器

## 新闻站点
目前支持以下新闻站点：
- [新浪中国](https://www.sina.com.cn/)
- [多维新闻](https://www.dwnews.com/) (墙外)
- [倍可亲](https://www.backchina.com/) (墙外)

## 安装
- 在server目录下，运行命令行 `pip install -r requirements.txt`
- 运行命令行`python -m spacy download zh_core_web_sm`
- 安装[油猴](https://www.tampermonkey.net/)浏览器插件
- 打开油猴控制面板，添加`client\news suggestion.user.js`脚本：
  - 点击Utilities栏，点Import Choose File，选择`client\news suggestion.user.js`
  - 点击Installed Script栏，如果脚本的状态是禁用，点击Enabled将其启用

## 运行
- server目录下，运行命令行 `python news_server.py`
- 打开浏览器，浏览支持的新闻站点

