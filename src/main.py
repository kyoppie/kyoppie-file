# coding: utf-8
import flask
import os.path
import mimetypes
import json
import utils
import magic
import PIL.Image
app = flask.Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16*1024*1024 #16M
def api(f):
    def wrap():
        r = f()
        c = r[1]
        r = flask.Response(json.dumps(r[0]))
        r.headers["Content-Type"] = "application/json"
        return r,c
    return wrap
@app.route('/')
def indexPage():
    return "kyoppie file server with python"
@app.route('/<path:filename>')
def fileShow(filename):
    if(filename.count("..")):
        return "Forbidden",403
    path = "../files/"+filename
    if(not os.path.exists(path)):
        return "Not Found",404
    f = open(path,"rb")
    d = f.read()
    f.close()
    return d
@app.route('/api/v1/upload',methods=["POST"])
@api
def apiV1Upload():
    file = flask.request.files.get("file")
    if(not file):
        return {"result":False,"error":"file-is-required"},400
    # とりあえずセーブ
    filename = "../upload_tmp/"+utils.get_temp_save_filename()
    file.save(filename)
    print(filename)
    # ファイルの種類を判断する
    path = "../files/"
    mimetype = magic.Magic(mime=True).from_file(filename).decode("utf-8")
    print(mimetype)
    img = None
    if(mimetype == "image/png" or mimetype == "image/bmp"): #可逆圧縮な画像ファイル
        new_filename = utils.get_filename("png")
        print(new_filename)
        img = PIL.Image.open(filename)
        img.save(path+new_filename,"png")
    elif(mimetype == "image/jpeg" or mimetype == "image/jpg"):
        new_filename = utils.get_filename("jpg")
        print(new_filename)
        img = PIL.Image.open(filename)
        img.save(path+new_filename,"jpeg",quality=80)
    else:
        return {"result":False,"error":"invalid-file"},400
    if(img):
        img.thumbnail(utils.get_resize_size(img.size))
        img.save(path+new_filename+".thumbnail.jpg","jpeg",quality=75)
    return {"result":False,"error":"not-implement"},503
    
app.run(port=4009,threaded=True,debug=True)