# -*- coding: UTF-8 -*-
import commands
import sys
from flask import Flask, request
import methods
from threading import Thread
import multiprocessing
import operator
import time
from argparse import ArgumentParser
from multiprocessing import Event
from multiprocessing import Pipe

from terminaltables import AsciiTable

from config import enable_chrome
from core.baiduzhidao import baidu_count
from core.check_words import parse_false
from core.chrome_search import run_browser

reload(sys)
sys.setdefaultencoding('utf-8')
app = Flask(__name__)


# @Author  : Skye
# @Time    : 2018/1/8 20:38
# @desc    : 答题闯关辅助，百度搜索

def parse_args():
    parser = ArgumentParser(description="Million Hero Assistant")
    parser.add_argument(
        "-t", "--timeout",
        type=int,
        default=5,
        help="default http request timeout"
    )
    return parser.parse_args()


def parse_question_and_answer(title, answers):
    # question = ""
    # start = 0
    # for i, keyword in enumerate(text_list):
    #     question += keyword
    #     if "?" in keyword:
    #         start = i + 1
    #         break
    real_question = title.split(".")[-1]
    question, true_flag = parse_false(real_question)
    return true_flag, real_question, question, answers


def pre_process_question(keyword):
    """
    strip charactor and strip ?
    :param question:
    :return:
    """
    for char, repl in [("“", ""), ("”", ""), ("？", "")]:
        keyword = keyword.replace(char, repl)

    keyword = keyword.split(r"．")[-1]
    keywords = keyword.split(" ")
    keyword = "".join([e.strip("\r\n") for e in keywords if e])
    return keyword


def __inner_job(title, answers):
    start = time.time()

    true_flag, real_question, question, answers = parse_question_and_answer(title, answers)
    print('-' * 72)
    print(real_question)
    print('-' * 72)
    print("\n".join(answers))

    # notice browser
    if enable_chrome:
        writer.send(question)
        noticer.set()

    search_question = pre_process_question(question)
    summary = baidu_count(search_question, answers, timeout=timeout)
    summary_li = sorted(
        summary.items(), key=operator.itemgetter(1), reverse=True)
    data = [("选项", "同比")]
    for a, w in summary_li:
        data.append((a, w))
    table = AsciiTable(data)
    print(table.table)

    print("*" * 72)
    if true_flag:
        print "肯定回答(**)：%s" % summary_li[0][0]
        print "否定回答(  )：%s " % summary_li[-1][0]
    else:
        print "肯定回答(  )： %s" % summary_li[0][0]
        print "否定回答(**)： %s" % summary_li[-1][0]

    print("*" * 72)
    end = time.time()
    print("use {0} 秒".format(end - start))
    # save_screen(
    #     directory=data_directory
    # )


def run_command(cmd):
    status, output = commands.getstatusoutput(cmd)
    return status, output


@app.route('/question', methods=['POST'])
def questionAndAnswer():
    data = request.json
    title = data["title"]
    answers = data["answer"]
    __inner_job(title, answers)
    m2 = Thread(methods.run_algorithm(1, title, answers))
    m3 = Thread(methods.run_algorithm(2, title, answers))
    m2.start()
    m3.start()
    return ""


if __name__ == '__main__':
    args = parse_args()
    timeout = args.timeout

    if enable_chrome:
        closer = Event()
        noticer = Event()
        closer.clear()
        noticer.clear()
        reader, writer = Pipe()
        browser_daemon = multiprocessing.Process(
            target=run_browser, args=(closer, noticer, reader,))
        browser_daemon.daemon = True
        browser_daemon.start()
    app.run(host="192.168.31.211", port=5000)
    if enable_chrome:
        reader.close()
        writer.close()
        closer.set()
        time.sleep(3)
