from MainServer.Managers import MainManager
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import sys
from flask_uploads import UploadSet, configure_uploads, ALL
from flask.helpers import send_from_directory
import os
import uuid

main_manager = MainManager()

application = Flask(__name__)
CORS(application, supports_credentials=True)
application.config['CORS_HEADERS'] = 'Content-Type'
photos = UploadSet('photos', ALL)
application.config['UPLOADED_PHOTOS_DEST'] = 'MainServer/static/images'
configure_uploads(application, photos)


@application.route('/<manager>/<user>/<request_function>', methods=['POST', 'GET', 'DELETE'])
def main_gateway(manager, user, request_function):
    print(f"{manager}, {user}, {request_function}")
    if request.method == 'GET':
        input_bundle = request.args.to_dict()
    else:
        try:
            input_bundle = request.json
        except:
            input_bundle = {}

    if "Token" in request.headers:
        token = request.headers["Token"]
    else:
        token = ""
    if "shop_id" in request.headers:
        shop_id = request.headers["shop_id"]
        input_bundle["shop_id"] = shop_id

    if input_bundle is None or type(input_bundle) == str:
        input_bundle = {}
    input_bundle["token"] = token
    manager_name = "{0}_manager".format(manager)
    function_name = "{0}_{1}".format(user, request_function)

    manager = getattr(main_manager, manager_name)
    result = manager.gateway(input_bundle, function_name)
    return jsonify(result), 200


@application.route('/upload', methods=['POST'])
def upload_admin():
    if 'file' in request.files:
        photo = request.files['file']

        image_id = "ImageID"
        image_id += uuid.uuid4().hex[:50]
        name = "{0}.{1}".format(image_id, photo.filename.rsplit('.', 1)[1].lower())
        address = request.base_url + "images/{0}".format(name)
        # address = address.replace('https', 'http')
        # address = address.replace('http', 'https')
        photos.save(photo, name=name)

        result = {
            "status": "ok",
            "code": 200,
            "farsi_message": "عکس با موفقیت آپلود شد.",
            "english_message": "image uploaded successfully.",
            "data": {
                "image_address": address
            }
        }
        return jsonify(result), 200


@application.route('/uploadimages/<path:filename>', methods=['GET'])
def get_images(filename):
    return send_from_directory(os.path.join(application.root_path, 'static', 'images'), filename)


if __name__ == '__main__':
    application.run(port=port, host='0.0.0.0', debug=True)
