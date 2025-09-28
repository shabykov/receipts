import json

import flask
import pydantic
from flask import Flask, request, jsonify
from flask_restful import Api, Resource

from internal.domain.receipt import ReceiptRecognizeError
from internal.domain.receipt.receipt_uuid import ReceiptUUID
from internal.domain.user.id import UserId
from internal.usecase.interface import IReceiptReadUC, IReceiptRecognizeUC
from .convert import convert

default_user_id = UserId(0)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename: str):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_file(req: flask.Request):
    if 'image' in req.files:
        return req.files['image']

    return req.files.get('file')


class Delivery:
    def __init__(
            self,
            receipt_reader_uc: IReceiptReadUC,
            receipt_recognizer_uc: IReceiptRecognizeUC,
            # flask attrs
            flask_app: Flask,
            flask_api: Api,
            host: str,
            port: int = 8080,
    ):
        self.receipt_reader_uc = receipt_reader_uc
        self.receipt_recognizer_uc = receipt_recognizer_uc

        self.flask = flask_app
        self.api = flask_api
        self.host = host
        self.port = port
        self.init_api()

    def start(self):
        self.flask.run(host=self.host, port=self.port, debug=True)

    def init_api(self):

        class ReceiptsResource(Resource):

            receipt_recognizer_uc = self.receipt_recognizer_uc

            def post(self):
                """
                Upload receipt API
                ---
                tags:
                  - Files
                consumes:
                  - multipart/form-data
                produces:
                  - application/json
                parameters:
                  - in: formData
                    name: file
                    type: file
                    required: true
                    description: Бинарный файл для загрузки
                  - in: formData
                    name: description
                    type: string
                    required: false
                    description: Доп. описание файла
                definitions:
                  ReceiptItem:
                    type: object
                    properties:
                      uuid:
                        type: string
                      product:
                        type: string
                      quantity:
                        type: integer
                      price:
                        type: number
                      created_at:
                        type: string
                  Receipt:
                    type: object
                    properties:
                      user_id:
                        type: integer
                      uuid:
                        type: string
                      store_name:
                        type: string
                      items:
                        type: array
                        items:
                          $ref: '#/definitions/ReceiptItem'
                responses:
                  200:
                    description: receipt
                    schema:
                      $ref: '#/definitions/Receipt'
                """

                file = get_file(request)
                if not file:
                    return jsonify({'error': 'No image part in the request'}), 400

                if file.filename == '':
                    return jsonify({'error': 'No selected file'}), 400
                if file and allowed_file(file.filename):
                    try:

                        receipt = self.receipt_recognizer_uc.recognize(default_user_id, convert(file))

                        return json.loads(receipt.model_dump_json()), 201  # TODO: fix receipt.model_dump()

                    except ReceiptRecognizeError as err:

                        return {'error': str(err)}, 400

                    except Exception as err:

                        return {'error': str(err)}, 400

                return {'error': 'Invalid file type'}, 400

        class ReceiptResource(Resource):

            receipt_reader_uc = self.receipt_reader_uc

            def get(self, receipt_id: str):
                """
                Receipt read API
                ---
                parameters:
                  - in: path
                    name: receipt_id
                    type: string
                    required: true
                definitions:
                  ReceiptItem:
                    type: object
                    properties:
                      uuid:
                        type: string
                      product:
                        type: string
                      quantity:
                        type: integer
                      price:
                        type: number
                      created_at:
                        type: string
                  Receipt:
                    type: object
                    properties:
                      user_id:
                        type: integer
                      uuid:
                        type: string
                      store_name:
                        type: string
                      items:
                        type: array
                        items:
                          $ref: '#/definitions/ReceiptItem'
                responses:
                  200:
                    description: receipt
                    schema:
                      $ref: '#/definitions/Receipt'

                """

                try:
                    uuid = ReceiptUUID(receipt_id)
                except pydantic.ValidationError as err:
                    return {'error': "input receipt_uuid is not valid: %s" % str(err)}, 400

                receipt = self.receipt_reader_uc.read(uuid)
                if receipt:
                    return json.loads(receipt.model_dump_json()), 200  # TODO: fix receipt.model_dump()

                return jsonify({"message": "not found"}), 404

        self.api.add_resource(ReceiptsResource, "/receipts")
        self.api.add_resource(ReceiptResource, "/receipts/<string:receipt_id>")
