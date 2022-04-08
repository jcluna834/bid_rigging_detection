__author__ = "Julio Luna"
__email__ = "jcluna834@gmail.com"

from controller.base import BaseController
from bson.objectid import ObjectId
from datetime import datetime
from enum import Enum
from flask import jsonify, request
from pymongo import MongoClient
from settings import app


client = MongoClient('localhost:27017')
__collection__ = 'PlagiarismDetection'

class BidRiggingDetection(BaseController):

    @app.route("/api/v1/bigrigging/executeBidRiggingAnalisis", methods=['POST'])
    def executeBidRiggingAnalisis():
        try:
            data = request.get_json()
            # Se obtiene la información del documento
            #Se crea el registro histórico de análisis
            #Status del documento a analizado
            #Se obtiene el entity_code
            #Se ejecuta el proceso de análsis de similitud
            #Status del histórico 
            #Envío del email
        except:
            #Se limpia el historico
            return jsonify(status_code=500, message='Error to analize document!')
        return jsonify(status_code=200, success=True, message='Return info match', data="response_analysis")
