from flask import Flask,render_template,request,redirect,url_for,session
from flask import send_from_directory
from bson.objectid import ObjectId
import pymongo
import os
import json
from nltk.corpus import stopwords
from elasticsearch import Elasticsearch
from pymongo import MongoClient
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
import json
import sqlite3 as lite
import sys

UPLOAD_FOLDER = 'uploaded'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
arr=[]
app = Flask(__name__)
app.secret_key = 'F12Zr47j\3yX R~X@H!jmM]Lwf/,?KT'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#ALLOWED_EXTENSIONS = set(['pdf'])

def sumSessionCounter():
  try:
    session['counter'] += 1
  except KeyError:
    session['counter'] = 1
@app.route('/')
def home():
	sumSessionCounter()
	return render_template("index.html")
@app.route("/register")
def register():
	return render_template("form-register.html")
@app.route("/search")
def search():
	#print "\n",res
	return render_template("search.html")
@app.route('/list', methods= ['POST','GET']) 
def list():   
	
	es=Elasticsearch()
	#es.index(index="db1",doc_type="pdfss",id=i,body=json)
	dsltype="match_all"
	b={}
	c={}
	c[dsltype]=b
	
	q={}
	q['query']=c
	print q
	res=es.search(index="db1",doc_type="pdfsss",body=q)
	#print res
	list=print_hits(res)
	print list
	return render_template("results.html",list=list)
@app.route('/results', methods= ['POST','GET']) 
def results():   
	want1=request.form['keyword']
	es=Elasticsearch()
	#es.index(index="db1",doc_type="pdfss",id=i,body=json)
	field1="author"
	field2="title"
	dsltype="multi_match"
	fuzziness="3"
	a={}
	#a['fuzziness']=3
	a['value']=want1
	#a['fuzziness']=3
	b={}
	b["query"]=want1
	b["fields"]=[ "author", "title","keywords","fname" ]
	#b["fuzziness"]="AUTO"
	#b["prefix_length"]=2
	c={}
	c[dsltype]=b
	
	q={}
	q['query']=c
	print q
	res=es.search(index="db1",doc_type="pdfss",body=q)
	#print res
	list=print_hits(res)
	print list
	return render_template("results.html",list=list)
def print_search_stats(results):
	print('=' * 80)
	list=[]
	for response in results['hits']['hits']:
		r={}
		for keys in response['_source'] :
			if keys != "keywords":
				r[keys]=response['_source'][keys]
		list.append(r);
	#print list
	#print('Total %d found in %dms' % (results['hits']['total'], results['took']))
	#print('-' * 80)
	return list

def print_hits(results):
	" Simple utility function to print results of a search query. "
	list=print_search_stats(results)
	#print('=' * 80)
	print()
	return list
@app.route("/download/<filename>", methods= ['POST','GET'])
def download(filename):
		
		add("downloads1",filename,"rahul",session["name"])
		uploads=os.path.join(UPLOAD_FOLDER)
		return send_from_directory(directory=uploads, filename=filename)
	
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
		return render_template("uploadverify.html",data=arr,filename=filename)
def list1(cat,uname,pas):
			con = lite.connect('test1.db')
			print cat,uname,pas
		
			with con:
				cur = con.cursor()
				cur.execute("SELECT * FROM users1 where email = '"+uname+"' and password = '"+pas+"';")

			rows = cur.fetchall()
			c=None
			for row in rows:
				#c=c+1
				c=row[0]
			return c		
@app.route('/login',methods= ['POST','GET']) 
def login():
  
  # if a name has been sent, store it on a session variable
  if request.method == 'POST':
	ename=request.form['email']
	pwd=request.form['password']
	tname="users1"
	print ename,pwd,tname
	c=list1(tname,ename,pwd)
	if c:
		print "creating sessions"
#		sumSessionCounter()
		session['name'] = c
		session['id']=ename
    # And then redirect the user to the main page
		return redirect(url_for('home'))
	else:
		print "Enter correctly"
  else:
    # If no name has been sent, show the form
	print "no name"
	return render_template('login.html', session=session)

@app.route('/clear')
def clearsession():
    
    session.clear()
   
    return redirect(url_for('home'))
@app.route("/processing/<filename>", methods= ['POST','GET'])
def processing(filename):
	field=['author','Creator','title','CreationDate','Producer']
	entry={}
	fpath = os.path.join(UPLOAD_FOLDER, filename)
	ftext=filename.replace('.pdf','.txt')
	cmd="pdf2txt -o "+ftext+" -t text  "+fpath 
	print "\n====",cmd
	os.system(cmd);
	entry["author"]=request.form["Author"]
	entry["title"]=request.form["Title"]
	entry["publisher"]=session["name"];
	
	entry["fname"]=filename
	
	put=" "
	
	with open(ftext,'r') as f:
		stop = stopwords.words('english')
		keyword=[]
		for line in f:
			for word in line.split():
				word=word.decode('utf-8')
				if word not in stop :
					if word not  in keyword:
						put+=word+" "				
	entry['keywords']=put
	print entry 
	js=json.dumps(entry)
	es=Elasticsearch()
	file1=open("count1.txt","r")
	count=file1.readlines();
	#print int(count[0])
	file1.close()

	count[0]=int(count[0])+1
	file1=open("count1.txt","w")
	file1.write('%d' % int(count[0]))
	file1.close()
	es.index(index="db1",doc_type="pdfsss",id=count[0],body=js)
	return redirect(url_for('list'))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS



@app.route("/contact")
def contact():
	return render_template("contact.html")
@app.route("/response",methods=['POST','get'])
def response():
	name=request.form['username']
	email=request.form['email']
	password=request.form['password']
	tbname="users1"
	add(tbname,name,email,password)
	return redirect(url_for('login'))


def add(cat,name,email,password):
		if cat is None:
                        print "pls enter the cat name"
		else:

			

			try:
				con = lite.connect('test1.db')

				cur = con.cursor()
				details = [(name,email,password)]
				print cat
				con.executemany('INSERT INTO '+cat+' VALUES (?,?,?)', details)
			#cur.executescript("INSERT INTO TABLE "+cat+" VALUES("+str(tid)+","+str(name)+","+str(desc)+","+str(date)+","+str(ranks)+");")

				con.commit()
				#list(cat)
			except lite.Error, e:

				if con:
					con.rollback()
    #print "Category already exists"    
					print "Error %s:" % e.args[0]
					sys.exit(1)

			finally:
				if con:
					con.close()

if __name__=='__main__':
	app.run(debug=True)

