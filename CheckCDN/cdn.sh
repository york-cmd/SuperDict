#!/bin/bash 
if [ "$#" -lt 1 ]; then
  echo "Error: At least three arguments are required."
  exit 1
fi


# 判断第一个变量是否存在，如果不存在则使用默认值
var1="${1:-请输入域名}"

# 判断第二个变量是否存在，如果不存在则使用默认值
var2="${2:-`date +"%Y-%m-%d-%H-%M-%S"`}"

# 判断第三个变量是否存在，如果不存在则使用默认值
var3="${3:-/root/gscan/result/tmp}"

if [ ! -d "$var3" ]; then
  mkdir -p $var3
fi
# 使用变量 var1、var2 和 var3
echo "var1: $var1"
echo "var2: $var2"
echo "var3: $var3"

datetime=$var2
# cd $dict_dir/CheckCDN
echo  $var1 | dnsx -retry 10 -json -r 8.8.8.8,223.5.5.5,119.29.29.29,114.114.114.114,1.1.1.1,1.0.0.1 -silent | ./nali > /tmp/test.json
python3 /root/gscan/SuperDict/CheckCDN/CheckCDN.py /tmp/test.json $datetime-out.json
jq -r '. | select(.iscdn == false and .isIntranetIP == false) | .a[]' "$datetime-out.json" >> $var3/$datetime-not-cdn-ips.txt
jq -r '. | select(.iscdn == false and .isIntranetIP == false) | .host' "$datetime-out.json" >> $var3/$datetime-not-cdn-domains.txt
jq -r '. | select(.iscdn == true and .isIntranetIP == false) | .host' "$datetime-out.json" >> $var3/$datetime-cdn-domains.txt
