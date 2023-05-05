import argparse
import json
import hashlib

# 定义命令行参数
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", help="input file path")
parser.add_argument("-o", "--output", help="output file path")
args = parser.parse_args()

# 打开输入文件并加载所有行
with open(args.input, "r") as f:
    lines = f.readlines()

# 创建一个空集合用于存储唯一的哈希值
unique_hashes = set()

# 循环遍历每一行 JSON 数据
for line in lines:
    # 将 JSON 字符串转换为 Python 字典
    data = json.loads(line)
    asn = data["asn"].get("as_number",[])
    # 提取需要计算的字段
    # body_md5 = data.get("hash", {}).get("body_md5[]", [])
    body_md5 = data["hash"]["body_md5"]
    words = data.get("words", [])
    webserver = data.get("webserver", [])
    a = data.get("a", [])
    status_code = data.get("status_code", [])
    content_length = data.get("content_length", [])
    title = data.get("title", [])
    lines = data.get("lines", [])
    # a = data["a"]


    # 计算新的哈希值
    only_md5 = hashlib.md5("{}{}{}{}{}{}{}{}{}".format(body_md5, words, webserver, a,status_code,content_length,title,lines,asn).encode()).hexdigest()

    # 将新字段添加到原始字典中
    data["only_md5"] = only_md5

    # 如果哈希值不在集合中，则将更新后的字典写入输出文件，并将哈希值添加到集合中
    if only_md5 not in unique_hashes:
        with open(args.output, "a") as f:
            f.write(json.dumps(data) + "\n")
        unique_hashes.add(only_md5)
