import time
from io import BytesIO

from requests import session
from PIL import Image
import PIL.ImageOps
import hashlib

def reg_img(file_obj,name):
    im = Image.open(file_obj)
    im = im.convert('L')
    binary_image = im.point([0 if i < 210 else 1 for i in range(256)], '1')
    im1 = binary_image.convert('L')
    im2 = PIL.ImageOps.invert(im1)
    im3 = im2.convert('1')
    im4 = im3.convert('L')
    im4.save("../testdata/{}.png".format(name))
    
#     im4.show()


veri_code_url = 'https://investorservice.cfmmc.com/veriCode.do?t=1601170214265'
ss = session()
for i in range(10):
    tmp_file = BytesIO()
    tmp_file.write(ss.get(veri_code_url).content)
    m = hashlib.md5()
    m.update(str(time.time()).encode())
    name = m.hexdigest()
    veri_code = reg_img(tmp_file,name)

