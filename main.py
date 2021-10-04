from datetime import date

from flask import Flask, jsonify, json, request, url_for, redirect, flash, send_from_directory, session, send_file, render_template, Response
from flask.wrappers import Response

from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy

from werkzeug.utils import secure_filename 
import os 

import random 
import json
import requests

"""
from elasticsearch import Elasticsearch, helpers
from elk_obj_create import Create_Elk_Obj
client = Create_Elk_Obj().get_elk_obj()
"""

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# @app.route("/<name>")
# def user(name):
#     return f"Hello {name}!"
#     #return "okay" 

# @app.route("/file-downloads/")
# def user(name):
#     return "test_data_1.mat"
#     #return "okay"

# if __name__ == "__main__":
#     app.run(host='0.0.0.0',port=9211)

# #url_for('static', filename='test_data_1.mat')
customer_put_args = reqparse.RequestParser()
customer_update_args = reqparse.RequestParser()

item_put_args = reqparse.RequestParser()
item_update_args = reqparse.RequestParser()

transaction_put_args = reqparse.RequestParser()
transaction_update_args = reqparse.RequestParser()

cpee_put_args = reqparse.RequestParser()
cpee_update_args = reqparse.RequestParser()

def define_arguments():
	customer_put_args.add_argument("name", type=str, help="Name of the customer is required", required=True)
	customer_put_args.add_argument("balance", type=float, help="Balance of the customer", required=True)

	customer_update_args.add_argument("name", type=str, help="Name of the customer is required")
	customer_update_args.add_argument("balance", type=float, help="Balance of the customer")

	item_put_args.add_argument("name", type=str, help="Name of the item is required", required=True)
	item_put_args.add_argument("price", type=float, help="Price of the item", required=True)
	item_put_args.add_argument("description", type=str, help="Description of the item is required", required=True)
	item_put_args.add_argument("stock", type=int, help="Stock of the item", required=True)

	item_update_args.add_argument("name", type=str, help="Name of the item is required")
	item_update_args.add_argument("price", type=float, help="Price of the item")
	item_update_args.add_argument("description", type=str, help="Description of the item is required")
	item_update_args.add_argument("stock", type=int, help="Stock of the item")

	transaction_put_args.add_argument("price", type=float, help="Price of the item", required=True)

	cpee_put_args.add_argument("url", type=str, help="Callback url", required=True)
	cpee_put_args.add_argument("processed", type=int, help="Callback processed", required=True)

	cpee_update_args.add_argument("url", type=str, help="Name of the customer is required")
	cpee_update_args.add_argument("processed", type=int, help="Balance of the customer")
	
UPLOAD_FOLDER= './uploaded-file'
ALLOWED_EXTENSIONS = {'txt', 'jpg', 'mat', 'doc', 'docx'}
app = Flask(__name__)

api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

app.secret_key = "super secret key"
app.config['SESSION_TYPE'] = 'filesystem'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

class HelloWorld(Resource):
	def get(self):
		return {'Hello':'world'}

class CustomerModel(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100), nullable=False)
	balance = db.Column(db.Float, nullable=True)

	def __repr__(self):
		return f"Customer(id = {id}, name = {name}, balance = {balance})"

class ItemModel(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100), nullable=False)
	price = db.Column(db.Float, nullable=True)
	description = db.Column(db.String(300), nullable=True)
	stock = db.Column(db.Integer, primary_key=False)

	def __repr__(self):
		return f"Item(id = {id}, name = {name}, price = {price}, description = {description}, stock = {stock})"

class TransactionModel(db.Model):
	id_customer = db.Column(db.Integer, primary_key=True)
	id_item = db.Column(db.Integer, primary_key=True)
	price = db.Column(db.Float, nullable=True)

	def __repr__(self):
		return f"Transaction(id_customer = {id_customer}, id_item = {id_item}, price = {price})"

class CallbackModel(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	url = db.Column(db.String(100), nullable=False)
	processed = db.Column(db.Integer, default = 0, nullable=False)
# ****************** run it at every beging when db has been changed ******************
#db.create_all()
# ****************** run it at every beging when db has been changed ******************

define_arguments()

resource_fields_customer = {
	'id': fields.Integer,
	'name': fields.String,
	'balance': fields.Float
}

resource_fields_item = {
	'id': fields.Integer,
	'name': fields.String,
	'price': fields.Float,
	'description': fields.String,
	'stock': fields.Integer,
}

resource_fields_transction = {
	'id_customer': fields.Integer,
	'id_item': fields.Integer,
	'price': fields.Float
}

resource_fields_cpee = {
	'id': fields.Integer,
	'url': fields.String,
	'processed': fields.Integer
}

class CustomerList(Resource):
	@marshal_with(resource_fields_customer)
	def get(self):
		result = CustomerModel.query.all()
		return result

class Customer(Resource):
	@marshal_with(resource_fields_customer)
	def get(self, customer_id):
		result = CustomerModel.query.filter_by(id=customer_id).first()
		# drink = Drink.query.get_or_404(id)
		if not result:
			abort(404, message="Could not find customer with that id")
		return result

	@marshal_with(resource_fields_customer)
	def put(self, customer_id):
		args = customer_put_args.parse_args()
		result = CustomerModel.query.filter_by(id=customer_id).first()
		if result:
			abort(409, message="Customer id taken...")

		customer = CustomerModel(id=customer_id, name=args['name'], balance=args['balance'])
		db.session.add(customer)
		db.session.commit()
		return customer, 201

	@marshal_with(resource_fields_customer)
	def post(self, customer_id):
		args = customer_update_args.parse_args()
		result = CustomerModel.query.filter_by(id=customer_id).first()
		if not result:
			abort(404, message="Customer doesn't exist, cannot update")

		if args['name']:
			result.name = args['name']
		if args['balance']:
			result.balance = args['balance']

		db.session.commit()
		return result

	# def post(self, video_id):
	# 	some_json = request.get_json()
	
	def delete(self, customer_id):
		#abort_if_video_id_doesnt_exist(video_id)
		result = CustomerModel.query.filter_by(id=customer_id).first()
		db.session.delete(result)
		db.session.commit()
		return '', 204

class ItemList(Resource):
	@marshal_with(resource_fields_item)
	def get(self):
		result = ItemModel.query.all()
		return result

class Item(Resource):
	@marshal_with(resource_fields_item)
	def get(self, item_id):
		result = ItemModel.query.filter_by(id=item_id).first()
		# drink = Drink.query.get_or_404(id)
		if not result:
			abort(404, message="Could not find item with that id")
		return result

	@marshal_with(resource_fields_item)
	def put(self, item_id):
		args = item_put_args.parse_args()
		result = ItemModel.query.filter_by(id=item_id).first()
		if result:
			abort(409, message="Item id taken...")

		item = ItemModel(id=item_id, name=args['name'], price=args['price'], description=args['description'], stock=args['stock'])
		db.session.add(item)
		db.session.commit()
		return item, 201

	@marshal_with(resource_fields_item)
	def post(self, item_id):
		args = item_update_args.parse_args()
		result = ItemModel.query.filter_by(id=item_id).first()
		if not result:
			abort(404, message="Item doesn't exist, cannot update")

		if args['name']:
			result.name = args['name']
		if args['price']:
			result.price = args['price']
		if args['description']:
			result.description = args['description']
		if args['stock']:
			result.stock = args['stock']

		db.session.commit()
		return result

	# def post(self, video_id):
	# 	some_json = request.get_json()
	
	def delete(self, item_id):
		#abort_if_video_id_doesnt_exist(video_id)
		result = ItemModel.query.filter_by(id=item_id).first()
		db.session.delete(result)
		db.session.commit()
		return '', 204

class TransactionList(Resource):
	@marshal_with(resource_fields_transction)
	def get(self):
		result = TransactionModel.query.all()
		return result

class Transaction(Resource):
	@marshal_with(resource_fields_transction)
	def get(self, id_customer, id_item):
		result = TransactionModel.query.filter_by(id_customer=id_customer, id_item=id_item).first()
		# drink = Drink.query.get_or_404(id)
		if not result:
			abort(404, message="Could not find transction with that id")
		return result

	@marshal_with(resource_fields_transction)
	def put(self, id_customer, id_item):
		args = transaction_put_args.parse_args()
		result = TransactionModel.query.filter_by(id_customer=id_customer, id_item=id_item).first()
		if result:
			abort(409, message="Transaction id taken...")

		transaction = TransactionModel(id_customer=id_customer, id_item=id_item, price=args['price'])
		db.session.add(transaction)
		db.session.commit()
		return transaction, 201

	@marshal_with(resource_fields_transction)
	def post(self, id_customer, id_item):
		args = transaction_put_args.parse_args()
		result = TransactionModel.query.filter_by(id_customer=id_customer, id_item=id_item).first()
		if not result:
			abort(404, message="Transaction doesn't exist, cannot update")

		if args['price']:
			result.price = args['price']

		db.session.commit()
		return result

	# def post(self, video_id):
	# 	some_json = request.get_json()
	
	def delete(self, id_customer, id_item):
		#abort_if_video_id_doesnt_exist(video_id)
		result = TransactionModel.query.filter_by(id_customer=id_customer, id_item=id_item).first()
		db.session.delete(result)
		db.session.commit()
		return '', 204

class CPEEList(Resource):
	@marshal_with(resource_fields_cpee)
	def get(self):
		result = CallbackModel.query.all()
		return result

class CPEE(Resource):
	@marshal_with(resource_fields_cpee)
	def get(self, cpee_id):
		result = CallbackModel.query.filter_by(id = cpee_id).first()
		# drink = Drink.query.get_orz_404(id)
		if not result:
			abort(404, message="Could not find item with that id")
		return result

	@marshal_with(resource_fields_cpee)
	def put(self, cpee_id):
		args = cpee_put_args.parse_args()
		result = CallbackModel.query.filter_by(id = cpee_id).first()
		if result:
			abort(409, message="Item id taken...")

		cpee = CallbackModel(id=cpee_id,  url = args['url'], processed = args['processed'])
		db.session.add(cpee)
		db.session.commit()
		return cpee, 201

	def delete(self, cpee_id):
		#abort_if_video_id_doesnt_exist(video_id)
		result = CallbackModel.query.filter_by(id=cpee_id).first()
		db.session.delete(result)
		db.session.commit()
		return '', 204

	@marshal_with(resource_fields_cpee)
	def post(self, cpee_id):
		args = cpee_update_args.parse_args()
		result = CallbackModel.query.filter_by(id=cpee_id).first()
		if not result:
			abort(404, message="Cpee doesn't exist, cannot update")

		if args['url']:
			result.url = args['url']
		if args['processed']:
			result.processed = args['processed']

		db.session.commit()
		return result

api.add_resource(HelloWorld, "/")
#api.add_resource(Customer, "/customer/<int:customer_id>", "/customer/<int:customer_id>/update1")
api.add_resource(Customer, "/customer/<int:customer_id>")
api.add_resource(CustomerList, "/customers")
api.add_resource(Item, "/item/<int:item_id>")
api.add_resource(ItemList, "/items")
api.add_resource(Transaction, "/transaction/<int:id_customer>/<int:id_item>")
api.add_resource(TransactionList, "/transactions")

api.add_resource(CPEE, "/cpee/<int:cpee_id>")
api.add_resource(CPEEList, "/cpees")

@app.route("/customer/update", methods=['GET', 'POST'])
@marshal_with(resource_fields_customer)
def update_customer():
	customer_id = request.args.get('customer_id')
	new_balance = request.args.get('new_balance')

	result = CustomerModel.query.filter_by(id=customer_id).first()
	result.balance = new_balance

	db.session.commit()
	return result
    
@app.route("/item/update", methods=['GET', 'POST'])
@marshal_with(resource_fields_item)
def update_item():
	item_id = request.args.get('item_id')
	new_stock = request.args.get('new_stock')

	result = ItemModel.query.filter_by(id=item_id).first()
	result.stock = new_stock
	
	db.session.commit()
	return result

@app.route("/cpee/update", methods=['GET', 'POST'])
@marshal_with(resource_fields_cpee)
def update_cpee():
	cpee_id = request.args.get('cpee_id')
	processed = request.args.get('processed')

	result = CallbackModel.query.filter_by(id=cpee_id).first()
	result.processed = processed
	
	db.session.commit()
	return result

@app.route("/transaction/update", methods=['GET', 'POST'])
@marshal_with(resource_fields_transction)
def put_transaction():
	id_customer = request.args.get('id_customer')
	id_item = request.args.get('id_item')
	result = TransactionModel.query.filter_by(id_customer=id_customer, id_item=id_item).first()
	if result:
		abort(409, message="Transaction id taken...")

	transaction = TransactionModel(id_customer=id_customer, id_item=id_item, price=request.args.get('price'))
	db.session.add(transaction)
	db.session.commit()
	return transaction, 201

@app.route("/logs",  methods=['POST'])
def get_log():
	print("----------")
	doc_list = []
	post_data = request.get_data()
	#print("post_data: ", post_data, flush=True) #--> with b'' 
	json_str = post_data.decode("UTF-8")
	str_start = json_str.find('{')
	str_end = json_str.rfind('}')
	json_str = json_str[str_start:str_end + 1]

	"""
	index_name = "log_test_2"
	try:
		cnt = Create_Elk_Obj().get_elk_count(index_name)
	except:
		cnt = 0
		print("This is a new index pattern", flush= True)
	
	doc = json_str.replace("True", "true")
	doc = doc.replace("False", "false")
	# convert the string to a dict object
	dict_doc = json.loads(doc)
	dict_doc["_id"] = cnt
	doc_list += [dict_doc]

	try:
		print ("\nAttempting to index the list of docs using helpers.bulk()")
		# use the helpers library's Bulk API to index list of Elasticsearch docs
		resp = helpers.bulk(
		client,
		doc_list,
		index = index_name,
		doc_type = "_doc"
		)
		# print the response returned by Elasticsearch
		print ("helpers.bulk() RESPONSE:", resp)
		print ("helpers.bulk() RESPONSE:", json.dumps(resp, indent=4))

	except Exception as err:
		# print any errors returned w
		## Prerequisiteshile making the helpers.bulk() API call
		print("Elasticsearch helpers.bulk() ERROR:", err)
		quit()
	"""

	#post_data_json = json.loads(json_str)
	#print("post_data_json: ", post_data_json, flush=True)
	print(json_str, flush=True)

	msg = "log received"
	print("----------")
	return msg, 200
 # parse request .requests()

@app.route("/check_difference", methods=['GET'])
def get_difference():
	# chance of empty 25%
	#items= ['BUC_VQ_3V3_sample=1[]_tambient=25[°C]_VQtyp=3.3[V]_TEMP=25[C]_variant=Water[]_VIN=3.62[V]_IQ=0[mA]_00001.mat', 'BUC_VQ_3V3_sample=1[]_tambient=25[°C]_VQtyp=3.3[V]_TEMP=25[C]_variant=Water[]_VIN=3.87[V]_IQ=0[mA]_00001.mat', 'BUC_VQ_3V3_sample=1[]_tambient=25[°C]_VQtyp=3.3[V]_TEMP=25[C]_variant=Water[]_VIN=3[V]_IQ=0[mA]_00001.mat', 'BUC_VQ_3V3_sample=1[]_tambient=25[°C]_VQtyp=3.3[V]_TEMP=25[C]_variant=Water[]_VIN=5.2[V]_IQ=0[mA]_00001.mat', ' ']
	items=['s1', 's2', ' ', ' ']
	#items = return {'Hello':'world'}
	#return_dic = {}
	#return_dic['update'] = random.choice(items)
	#return json.dumps(return_dic)
	return_string = '{"update":' + '"' + random.choice(items) + '"' + '}'
	#return return_string
	return json.loads(return_string), {'Content-Type': 'application/json; charset=utf-8'}

	#response = make_response(jsonify({"message": str(FLAMSG_ERR_SEC_ACCESS_DENIED), "severity": "danger"}),200,)
	
@app.route("/hardcoded_response", methods=['GET'])
def get_hardcoded_response():
	return {'return':'HardcodedValue'}

@app.route("/asnyc_request", methods=['GET'])
def async_test():
	resp = Response("Foo bar baz")
	resp.headers['CPEE-CALLBACK'] = 'true'
	url_callback = request.headers.get('Cpee-Callback')

	list_list_Class = CallbackModel.query.all()
	cnt = len(list_list_Class)
	result = CallbackModel.query.filter_by(id=cnt).first()
	#item = CallbackModel(id=0,  url=request.headers.get('Cpee-Callback')),
	# cpee = CallbackModel(id=cpee_id,  url = args['url'])
	cpee = CallbackModel(id=cnt,  url = url_callback, processed =0)
	db.session.add(cpee)
	db.session.commit()
	return resp

@app.route("/asnyc_return", methods=['GET'])
def async_return():
	return_dict = "{\"value\", \"x\"}"

	return_callback = CallbackModel.query.filter_by(id=1).first()
	# drink = Drink.query.get_orz_404(id)
	#r = requests.put(url, data = return_dict, headers={"content-type": "application/json; charset=utf-8","CPEE-UPDATE": "true"})
	r = requests.put(return_callback.url, data = return_dict, headers={"content-type": "application/json; charset=utf-8"})
	#r = requests.put(ccu, data=json.dumps(payload), headers={"content-type": "application/json; charset=utf-8","CPEE-UPDATE": "true"})
	return {'Tast':'Continue'}

@app.route("/ask_user", methods=['GET'])
def ask_user():
	return_dic = {}
	#return_dic['x'] = request.args.get("x")
	#return_dic['y'] = request.args.get("y")
	return_dic['work'] = 'BUC_VQ_3V3_sample=1[]_tambient=25[°C]_VQtyp=3.3[V]_TEMP=25[C]_variant=Water[]_VIN=3.62[V]_IQ=0[mA]_00001.mat'
	return render_template('hello.php', input = return_dic)

@app.route("/interface", methods=['GET'])
def interface():
	return_dic = {}
	#return_dic['x'] = request.args.get("x")
	#return_dic['y'] = request.args.get("y")
	return_callback = CallbackModel.query.filter_by(id=1).first()
	return_dic['work'] = 'BUC_VQ_3V3_sample=1[]_tambient=25[°C]_VQtyp=3.3[V]_TEMP=25[C]_variant=Water[]_VIN=3.62[V]_IQ=0[mA]_00001.mat'
	list_Class = CallbackModel.query.all()
	list_url = []
	list_id = []
	for item in list_Class:
		if item.processed != 1:
			list_id.append(item.id)
			list_url.append(item.url)
	#return render_template('inter.html', working_item = return_dic['work'], url = return_callback.url)
	return render_template('inter.html', working_item = return_dic['work'], ids = list_id, urls = list_url)

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    
@app.route('/shutdown', methods=['GET'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'
    
if __name__ == "__main__":
    #sess = session.Session()
    #sess.init_app(app)
    app.run(host='0.0.0.0',port=9211, debug=True)
	#app.run(debug=True)
























# @app.route("/")
# def home():
#     return jsonify(hello="world")

# @app.route('/upload', methods=['GET', 'POST'])
# def upload_file():
#     if request.method == 'POST':
#         # check if the post request has the file part
#         if 'file' not in request.files:
#             flash('No file part')
#             return redirect(request.url)
#         file = request.files['file']
#         # If the user does not select a file, the browser submits an
#         # empty file without a filename.
#         if file.filename == '':
#             flash('No selected file')
#             return redirect(request.url)
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#             #return redirect(url_for('download_file', name=filename))
#             return "file has been uploaded"
#     return '''
#     <!doctype html>
#     <title>Upload new File</title>
#     <h1>Upload new File</h1>
#     <form method=post enctype=multipart/form-data>
#       <input type=file name=file>
#       <input type=submit value=Upload>
#     </form>
#     '''

# @app.route('/downlaod/<name>')
# def download_file(name):
#     return send_from_directory(app.config["UPLOAD_FOLDER"], name)
#     #send_file(path, as_attachment=True)

# @app.route('/downlaod/sendfile/<name>')
# def download_file_send_file(name):
#     return send_file(app.config["UPLOAD_FOLDER"] + name, as_attachment=True)
#     #send_file(path, as_attachment=True)
