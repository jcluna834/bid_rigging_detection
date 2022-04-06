__author__ = "Julio Luna"
__email__ = "jcluna834@gmail.com"

from flask import request
from util.response import intercept, Response
from controller.base import BaseController
from util.injector import inject
from service.plag_dao import PlagiarismDAO
from settings import app, config
import os
from werkzeug.utils import secure_filename
from flask import jsonify
from datetime import datetime
import pandas as pd
from pymongo import MongoClient

client = MongoClient('localhost:27017')
__collection__ = 'PlagiarismDetection'


UPLOAD_FOLDER = os.path.abspath(os.getcwd()) + '/documents'
ALLOWED_EXTENSIONS = {'pdf', 'xlsx', 'xls'}
config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def getCurrentUser():
    return config['USERAUTHID']

def getCurrentAnnouncement():
    return config['ANNOUNCEMENTID']

class Document(BaseController):
    plag_dao: PlagiarismDAO = inject(PlagiarismDAO)

    def __init__(self):
        self.events = []

    @intercept()
    def post(self, *args, **kwargs):
        """Adds a new document to repo"""
        data = request.get_json(force=True)
        return self.saveDocument(data, "save")

    @intercept()
    def get(self):
        """
        Fetches all the documents(paginated).
        :return:
        """
        res = self.plag_dao.get_docs_info(page=int(request.args.get("page", 1)),
                                    per_page=int(request.args.get("per_page", 10)), all='all' in request.args)
        
        docs_info = dict(data=[d for d in res['data']], count=res['count'])
        return Response(data=docs_info)

    @intercept()
    def put(self, *args, **kwargs):
        """Adds a new document to repo"""
        data = request.get_json(force=True)
        return self.saveDocument(data, "update")

    @intercept()
    def delete(self, *args, **kwargs):
        try:
            id = request.get_json()
            #Marcar como eliminado el documento
            self.plag_dao.deleteDocument(id)
            #Marcar como eliminado el registro del documento similar
            self.similarDocDao.deleteDocument(id)
            #Marcar loas análsisi como eliminados
            self.analysisHistoryDao.deleteAnalysis(id)
            #Eliminar el documento del índice
            self.elasticsearhobj.delete_by_query(id)
        except:
            return Response(status_code=500, message='Error to delete Document!')
        return Response(status_code=201, message='Document deleted successfully!')
    
    @app.route("/api/v1/bigrigging/uploadFile", methods=['GET','POST'])
    def upload_file():
        if request.method == 'POST':
            # check if the post request has the file part
            if 'file' not in request.files:
                return jsonify(status_code=500, message='No file part!')
            file = request.files['file']
            # If the user does not select a file, the browser submits an
            # empty file without a filename.
            if file.filename == '':
                return jsonify(status_code=500, message='No selected file!')
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(config['UPLOAD_FOLDER'], filename))

                try:
                    doc = Document()
                    #doc.saveDocument(data, "save")
                    
                    #get info file
                    data_xls = pd.read_excel(file)
                    val_totals = data_xls['Total'].tolist()
                    data_json = data_xls.to_dict(orient='record')

                    # Respuesta final entregada en el POST
                    super_res_data = {
                        'productsInfo': data_json,
                        'responsibleCode': getCurrentUser(),
                        'announcementCode': getCurrentAnnouncement(),
                        'documentID': "documentId",
                        'entityID': 1,
                        'AnalysisDate': datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                        'Total': sum(val_totals)
                    }
                    # Save in collection MongoDB
                    db = client.get_database(__collection__)
                    collection = db.BidRiggingDetection
                    collection.insert_one(super_res_data)

                except:
                    #TODO - validar que el documento no exista previamente para eliminar / agregar
                    os.remove(os.path.join(config['UPLOAD_FOLDER'], filename))
                    return jsonify(status_code=500, message='Error to save document in BD or Mongo!')
                return jsonify(status_code=201, message='Document added successfully!')
        return '''
        <!doctype html>
        <title>Upload new File</title>
        <h1>Upload new File</h1>
        <form method=post enctype=multipart/form-data>
        <input type=file name=file>
        <input type=submit value=Upload>
        </form>
        '''