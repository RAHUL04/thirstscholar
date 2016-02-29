from flask import Flask,render_template,request,redirect,url_for,session
from flask import send_from_directory
from bson.objectid import ObjectId
import pymongo
import os
from pymongo import MongoClient
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
import json

UPLOAD_FOLDER = 'uploaded'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
arr=[]
app = Flask(__name__)
app.secret_key ='rahulgauthammuralipusa'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app=Flask(__name__)
#ALLOWED_EXTENSIONS = set(['pdf'])
@app.route('/')
def home():
	return render_template("index.html")
@app.route("/register")
def register():
	return render_template("form-register.html")
@app.route("/search")
def search():
	return render_template("search.html")

@app.route("/upload", methods= ['POST','GET'])
def upload():
	return render_template("upload.html")
@app.route('/give', methods= ['POST','GET']) 
def give():        
	file = request.files['imagefile']
	if file and allowed_file(file.filename):
		filename = file.filename
		file.save(os.path.join(UPLOAD_FOLDER, filename))
		pd=open(UPLOAD_FOLDER +'/'+ filename,'rb')
		parser=PDFParser(pd)
		doc = PDFDocument(parser)
		parser.set_document(doc)
		jsondata=doc.info
		arr=jsondata[0]
		print arr
		return render_template("uploadverify.html",data=arr)
		
@app.route('/login')
def login():
  #sumSessionCounter()
  # if a name has been sent, store it on a session variable
  if request.args.get('yourname'):
    session['name'] = request.args.get('yourname')
    # And then redirect the user to the main page
    return redirect(url_for('home'))
  else:
    # If no name has been sent, show the form
    return render_template('login.html', session=session)
@app.route("/putinmongo", methods= ['POST','GET'])
def putinmongo():
	client=MongoClient('localhost',27017)
	db=client.test
#	c_name="users"
	c_name=db.filess
	field=['Author','Creator','Title','CreationDate','Producer']
	entry={}
	for key in field:
		entry[key]=request.form[key]
	print entry
	c_name.insert_one(entry)
	d=c_name.find()
	print "database"
	print d
	return render_template("filesgiven.html",rows=d)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS



@app.route("/contact")
def contact():
	return render_template("contact.html")
@app.route("/response",methods=['post','get'])
def response():
	name=request.form['inputName']
	email=request.form['inputEmail']
	passwd=request.form['inputPassword']
	client=MongoClient('localhost',27017)
	db=client.test
#	c_name="users"
	c_name=db.users
	entry={"name":name,"email":email,"password":passwd}
	c_name.insert_one(entry)
	
	return redirect(url_for('home'))
if __name__=='__main__':
	app.run(debug=True)

