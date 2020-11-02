import time
from io import BytesIO

from requests import session
from PIL import Image
import PIL.ImageOps

import pandas as pd
import collections,csv
import numpy as np
from keras.preprocessing import image
from keras.models import load_model
from bs4 import BeautifulSoup
import os

if not os.path.exists("/home/output/"):
    os.makedirs(path) 


def reg_img(file_obj):
    im = Image.open(file_obj)
    im = im.convert('L')
    binary_image = im.point([0 if i < 210 else 1 for i in range(256)], '1')
    im1 = binary_image.convert('L')
    im2 = PIL.ImageOps.invert(im1)
    im3 = im2.convert('1')
    im4 = im3.convert('L')
    im4.save("_tmp.png")
    
    colorChannel = 3
    height,width = 32,100
    characters = '0123456789abcdefghijklmnopqrstuvwxyz'
    modelpath =  "{}/../bzjjkzx.h5".format(os.path.dirname(os.path.abspath(__file__)))
    
    X = np.zeros((1, height, width, colorChannel), dtype=np.uint8)
    X[0] = image.load_img("_tmp.png", target_size=(height, width))
    
    result = ''
    XXX = np.array(X)
    model = load_model(modelpath)
    
    for i in model.predict(XXX):
        result += characters[np.argmax(i)]
        
    return result

def flag_filter(content, flag):
    result = content.split(flag)[1].split('"')[0]
    return result

def get_current_equity(content):
    a = content[content.find('客户权益'):]
    b = a.split('<td class="table-normal-text" align="right">')[1]
    c = b[:b.find('&nbsp;')].strip()
    d = ''.join(c.split(','))
    return float(d)

def pharseinfo(df):
    '''
    '''
    title = df.columns.values[0]
    rst = collections.OrderedDict()
    for line in df.values:
        for k,v in zip(line[::2],line[1::2]):
            if k is not None:
                rst[k] = v
    return title,rst

def save_to_csv(rst):
    
    account = rst["基本资料"]["客户期货期权内部资金账户"]
    name = rst["基本资料"]["客户名称"]
    current_equity = rst["期货期权账户资金状况"]["客户权益"]
    print("客户账户:{}   客户权益:{}".format(account,current_equity))
    rst["基本资料"]["客户名称"] = "******"
    rst["基本资料"]["期货公司名称"] = "******"
    fields = ["基本资料","期货期权账户资金状况"] 
    with open("/home/output/{}.csv".format(account),"w",newline='',encoding="utf8") as csvfile: 
        writer = csv.writer(csvfile)
        for block_name in fields:
            block_values = rst[block_name]
            writer.writerow([block_name])
            for items in block_values.items():
                writer.writerow(items)
            writer.writerow("")
            writer.writerow("")

def do(user_id, passwd):
    header = {
        'Connection': 'keep-alive',
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
    }
    url = "https://investorservice.cfmmc.com/login.do"
    token_flag = 'name="org.apache.struts.taglib.html.TOKEN" value="'
    veri_code_flag = 'src="/veriCode.do?t='
    ss = session()
    res = ss.get(url, headers=header)
    content = res.content.decode()
#     token = flag_filter(content, token_flag)
    veri_code_url = 'https://investorservice.cfmmc.com/veriCode.do?t=' + flag_filter(content, veri_code_flag)
    for i in range(10):
        print("第{}次验证码识别".format(i))
        tmp_file = BytesIO()
        tmp_file.write(ss.get(veri_code_url).content)
        veri_code = reg_img(tmp_file)
        print(veri_code)
        if veri_code and len(veri_code) == 6:
            veri_code = ''.join(filter(str.isalnum, veri_code))
            print('\t验证码：', veri_code)
            post_data = {
    #                 "org.apache.struts.taglib.html.TOKEN": token,
                "showSaveCookies": '',
                "userID": user_id,
                "password": passwd,
                "vericode": veri_code,
            }
            content2 = ss.post(url, data=post_data, headers=header, timeout=5)
            res = content2.content.decode()
            html=pd.read_html(res,header=0)
            if "验证码错误" not in res:
                rst = collections.OrderedDict( pharseinfo(html[i]) for i in range(len(html)))
                save_to_csv(rst)
                return
            else:
                time.sleep(1)
                veri_code_url = "https://investorservice.cfmmc.com/veriCode.do?t=" + str(int(time.time() * 1000))
    print('爬取客户权益 失败')

if __name__ == '__main__':
    import os
    account = os.environ.get('ACCOUNT',"")
    password = os.environ.get('PASSWD',"")
    
    do(account, password)






