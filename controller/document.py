__author__ = "Julio Luna"
__email__ = "jcluna834@gmail.com"

from flask import request, send_file
from util.response import intercept, Response
from controller.base import BaseController
from util.injector import inject
from service.bid_rigging_dao import BidRiggingDAO
from settings import app, config
import os
from werkzeug.utils import secure_filename
from flask import jsonify
from datetime import datetime
import pandas as pd
from pymongo import MongoClient
from util.error_handlers.exceptions import ExceptionBuilder, BadRequest
from util.constants.error_codes import HttpErrorCode

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

def getCurrentEntity():
    return config['ENTITYID']

class Document(BaseController):
    bid_rigging_dao: BidRiggingDAO = inject(BidRiggingDAO)

    def __init__(self):
        self.events = []

    def saveDocument(self, data, option):
        title = data.get('title', '')
        fileName = data.get('fileName', '')
        description = data.get('description', '')
        responsibleCode = data.get('responsibleCode', '')
        announcementCode = data.get('announcementCode', '')
        documentType = data.get('documentType', '')

        if title:
            try:
                # Se agrega el documento en la BD
                if (option == "save"):
                    # Se agrega el documento en la BD
                    doc = self.bid_rigging_dao.create_doc("", title, fileName, description=description, responsibleCode=responsibleCode, announcementCode=announcementCode, documentType=documentType)
                    message='Economic document added successfully!'
                else:
                    id = data.get('id', '')
                    doc = self.bid_rigging_dao.edit_doc(id, title, description=description, responsibleCode=responsibleCode, announcementCode=announcementCode)
                    message='Economic document updated successfully!'
            except:
                return Response(status_code=500, message='Error to delete Document!', data=[])

        else:
            ExceptionBuilder(BadRequest).error(HttpErrorCode.REQUIRED_FIELD, 'title').throw()

        return Response(status_code=201, message=message, data=doc.to_dict_es())

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
        res = self.bid_rigging_dao.get_docs_info()
        
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
    
    @app.route('/api/v1/bidrigging/downloadFile/<path:filename>', methods=['GET', 'POST'])
    def download(filename):
        path = os.path.join(config['UPLOAD_FOLDER'], filename)
        return send_file(path, as_attachment=True)

    @app.route("/api/v1/bidrigging/uploadFile", methods=['GET','POST'])
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
                    data =  {
                        'title':request.form.get("title"), 
                        'description':request.form.get("description"), 
                        'fileName':filename,
                        'responsibleCode':request.form.get("responsibleCode"), 
                        'announcementCode':request.form.get("announcementCode"),
                        'documentType':request.form.get("documentType")
                    }
                    response = doc.saveDocument(data, "save")
                    
                    if(response.status_code == 201):
                        #get info file
                        data_xls = pd.read_excel(file)
                        val_totals = data_xls['Total'].tolist()
                        data_json = data_xls.to_dict(orient='record')

                        # Respuesta final entregada en el POST
                        super_res_data = {
                            'productsInfo': data_json,
                            'responsibleCode': getCurrentUser(),
                            'announcementCode': request.form.get("announcementCode"),
                            'documentID': response.data.get('id'),
                            'entityID': getCurrentEntity(),
                            'AnalysisDate': datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                            'Total': sum(val_totals)
                        }
                        # Save in collection MongoDB
                        db = client.get_database(__collection__)
                        collection = db.BidRiggingDetection
                        collection.insert_one(super_res_data)
                    else:
                        return jsonify(status_code=500, message='Error to save document in BD or Mongo!')

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