#!/usr/bin/python3
# python3 head-scan.py
import socket,os,sys,threading,queue,time,random,requests,warnings,chardet,re
from datetime import date
import tldextract
import base64
import argparse

num = 0
Flag = False
warnings.filterwarnings("ignore")
class Checker:
    inputQueue = queue.Queue()
    def parse_args(self):
        parser = argparse.ArgumentParser(description='Process some input and output files.')
        parser.add_argument('-f', '--input_file', type=str, help='input file name')
        parser.add_argument('-o', '--output_file', type=str, required=True, help='output file name')
        parser.add_argument('-d', '--domain', type=str, help='Single domain to check')

        return parser.parse_args()
    def __init__(self):
        args = self.parse_args()
        self.domain = args.domain  # 单个域名参数
        self.leads = args.input_file if not self.domain else None
        self.threads = 100
        if self.leads:
            self.length = len(list(open(self.leads, encoding='utf-8')))
        else:
            self.length = 1  # 如果是单个域名，长度设置为1
    def get_result(self, data):
        results = []
        info = re.findall("<tbody><tr>(.*)</tr>", data)
        if not info:  # 检查info是否为空
            return results  # 如果为空，直接返回空结果列表
        for item in info[0].split("</tr>"):
            try:
                subdomain = item.split("<td>")[1].replace("</td>", "")
                results.append(subdomain)
            except IndexError as e:  # 捕获IndexError
                print(f"IndexError: {e}, item: {item}")
            except Exception as e:  # 捕获其他类型的异常
                print(f"Error: {e}, item: {item}")
        return results

    def save_to_fie(self, results):
        args = self.parse_args()
        kl1 = open(args.output_file, "a+")
        for item in results:
            kl1.writelines(item+"\n")
        kl1.close()
    def save_except(self, results):
        kl1 = open("except.txt", "a+")
        #for item in results:
        kl1.writelines(results+"\n")
        kl1.close()

    def send(self, domain):
        url = "https://rapiddns.io/subdomain/"+domain+"?full=1"
        headers = {
                'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
                'Upgrade-Insecure-Requests':'1','Connection':'keep-alive','Cache-Control':'max-age=0',
                'Accept-Encoding':'gzip, deflate, sdch','Accept-Language':'zh-CN,zh;q=0.8'
        }
        try:
            r = requests.get(url, verify=False, timeout=10)
            body = r.text
            result = self.get_result(body.replace("\r", "").replace("\n", ""))
            self.save_to_fie(result)
        except:
            print(sys.exc_info(), domain)
            self.save_except(domain)
            pass
            
    def check(self):
        global num
        global l
        while 1:
            target = self.inputQueue.get()
            num += 1
            if num % 100 == 0:
                print(f"({num}\{self.length})")
            self.send(target)
        # def run_thread(self):
    #     for x in range(int(self.threads)):
    #         t = threading.Thread(target=self.check)
    #         t.setDaemon(True)
    #         t.start()
    #     for y in open(self.leads, 'r', encoding='utf-8').readlines():
    #         self.inputQueue.put(y.strip())
    #         while True:
    #             if self.inputQueue.qsize() <= 1000:
    #                 break
    #             else:
    #                 time.sleep(5)
    #     while True:
    #         time.sleep(10)
    #         if self.inputQueue.qsize() == 0:
    #             break

    def run_thread(self):
        for x in range(int(self.threads)):
            t = threading.Thread(target=self.check)
            t.setDaemon(True)
            t.start()
        if self.domain:  # 如果指定了单个域名
            self.inputQueue.put(self.domain.strip())
        else:  # 否则，从文件中读取域名
            for y in open(self.leads, 'r', encoding='utf-8').readlines():
                self.inputQueue.put(y.strip())
                while True:
                    if self.inputQueue.qsize() <= 1000:
                        break
                    else:
                        time.sleep(5)
        while True:
            time.sleep(10)
            if self.inputQueue.qsize() == 0:
                break
      
if __name__=="__main__":
    start = Checker()
    #for domain in open('domain.txt'):
    #    start.send(domain.strip())
    start.run_thread()
