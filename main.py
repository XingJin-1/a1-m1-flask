from flask import Flask, jsonify, json, request, url_for, redirect, flash, send_from_directory, session, send_file
from flask.wrappers import Response

from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy

from werkzeug.utils import secure_filename 
import os 

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

class VideoModel(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100), nullable=False)
	views = db.Column(db.Integer, nullable=False)
	likes = db.Column(db.Integer, nullable=False)

	def __repr__(self):
		return f"Video(name = {name}, views = {views}, likes = {likes})"

#db.create_all()
video_put_args = reqparse.RequestParser()
video_put_args.add_argument("name", type=str, help="Name of the video is required", required=True)
video_put_args.add_argument("views", type=int, help="Views of the video", required=True)
video_put_args.add_argument("likes", type=int, help="Likes on the video", required=True)

video_update_args = reqparse.RequestParser()
video_update_args.add_argument("name", type=str, help="Name of the video is required")
video_update_args.add_argument("views", type=int, help="Views of the video")
video_update_args.add_argument("likes", type=int, help="Likes on the video")

resource_fields = {
	'id': fields.Integer,
	'name': fields.String,
	'views': fields.Integer,
	'likes': fields.Integer
}

class Video(Resource):
	@marshal_with(resource_fields)
	def get(self, video_id):
		result = VideoModel.query.filter_by(id=video_id).first()
		# drink = Drink.query.get_or_404(id)
		if not result:
			abort(404, message="Could not find video with that id")
		return result

	@marshal_with(resource_fields)
	def get(self):
		result = VideoModel.query.all()
		return result

	@marshal_with(resource_fields)
	def put(self, video_id):
		args = video_update_args.parse_args()
		result = VideoModel.query.filter_by(id=video_id).first()
		if result:
			abort(409, message="Video id taken...")

		video = VideoModel(id=video_id, name=args['name'], views=args['views'], likes=args['likes'])
		db.session.add(video)
		db.session.commit()
		return video, 201

	@marshal_with(resource_fields)
	def patch(self, video_id):
		args = video_update_args.parse_args()
		result = VideoModel.query.filter_by(id=video_id).first()
		if not result:
			abort(404, message="Video doesn't exist, cannot update")

		if args['name']:
			result.name = args['name']
		if args['views']:
			result.views = args['views']
		if args['likes']:
			result.likes = args['likes']

		db.session.commit()
		return result

	# def post(self, video_id):
	# 	some_json = request.get_json()
		
	def delete(self, video_id):
		#abort_if_video_id_doesnt_exist(video_id)
		result = VideoModel.query.filter_by(id=video_id).first()
		db.session.delete(result)
		db.session.commit()
		return '', 204

api.add_resource(Video, "/video/<int:video_id>", "/videos")
api.add_resource(HelloWorld, "/")

if __name__ == "__main__":
    #sess = session.Session()
    #sess.init_app(app)
    #app.run(host='0.0.0.0',port=9211)
	app.run(debug=True)
    


























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