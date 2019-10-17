from flask import Flask, redirect,url_for, flash,request,render_template
from werkzeug.utils import secure_filename
import pymysql,os,json,cv2
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from my_func import *

host = "127.0.0.1"

app = Flask(__name__)
app.secret_key = 'some_secret'

@app.route('/', methods= ['POST', 'GET'])
def index():
    #if request.method == 'POST':
    return render_template('index.html')

@app.route('/set_book',methods = ['POST', 'GET'])
def set_book():
    if request.method == 'POST':
        # 将上传的文件保存在服务器里面
        f = request.files['imgOne']
        basepath = os.path.dirname(__file__)  # 当前文件所在路径
        upload_path = os.path.join(
 				          './static/images/', 
                          secure_filename(f.filename)) 
        nnn = secure_filename(f.filename)
        f.save(upload_path)
        select = request.form.get('ssvalue')		
        print(select)
        if select == "1":
            img = cv2.imread(upload_path,0)
            O = my_gamma(img)
        elif select == "2":    
            img = cv2.imread(upload_path)
            O = my_segment(img)
        elif select == "3":    
            img = cv2.imread(upload_path, 0)
            O = my_distance(img)
        elif select == "4":    
            img = cv2.imread(upload_path, 0)
            O = my_binary(img)
        
        img_p_path = "./static/images/"+str(nnn[:-4])+"0"+str(nnn[-4:])
        aa = "./static/images/"+ str(secure_filename(f.filename))
        
        if select == "3":  
            plt.figure("Image1")
            plt.imshow(O, cmap="gray")
            plt.savefig(img_p_path)
        else:  
            cv2.imwrite(img_p_path, O)        
        return render_template('set_book.html', name1 = aa, name2 = img_p_path)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8090)
