__author__ = "Julio Luna"
__email__ = "jcluna834@gmail.com"

from math import prod
from controller.base import BaseController
from flask import jsonify, request
from pymongo import MongoClient
from settings import app, config
from scipy.stats import kurtosis
from util.injector import inject
from service.bid_detector import BidRiggingDetector
from datetime import datetime


client = MongoClient('localhost:27017')
__collection__ = 'PlagiarismDetection'

def getCurrentUser():
    return config['USERAUTHID']

def getCurrentEntity():
    return config['ENTITYID']
class BidRiggingDetection(BaseController):
    bid_detector: BidRiggingDetector = inject(BidRiggingDetector)

    def __init__(self):
        self.events = []

    @app.route("/api/v1/bidrigging/detect/executeBidRiggingAnalisis", methods=['POST'])
    def executeBidRiggingAnalisis():
        try:
            bidRiggingController = BidRiggingDetection()
            data = request.get_json()
            announcementCode = data['announcementCode']

            # Se obtiene la información del documento
            db = client.get_database(__collection__)
            collection = db.BidRiggingDetection
            responseCollection = collection.find({"responsibleCode": getCurrentUser(), "announcementCode": announcementCode})
            proposals = list(responseCollection)
            totals = [proposal["Total"] for proposal in proposals]
            douments = [proposal["documentID"] for proposal in proposals]

            # Se obtiene los cáclulos totales de cada propuesta
            totalAnalysis = bidRiggingController.bid_detector.calculateMeasures(totals)

            # Se obtiene los cáclulos de cada producto de cada propuesta
            productsInfo = proposals[0]["productsInfo"]
            productsDict = {}
            products = []
            for product in productsInfo:
                productsList = []
                for proposal in proposals:
                    for prod in proposal["productsInfo"]:
                        if prod["Identificación"] == product["Identificación"]:
                            productsList.append(prod["Total"])
                            break
                    productsDict = {"PROD_ID": product["Identificación"], "PROD_LIST": productsList}
                products.append(productsDict)
            
            anaylisis_prod = []
            for product in products:
                response = bidRiggingController.bid_detector.calculateMeasures(product["PROD_LIST"])
                data = {
                    'PROD_ID': product['PROD_ID'],
                    'PROD_LIST': product["PROD_LIST"],
                    'Anaylis': response
                }
                anaylisis_prod.append(data)
                    
            # Respuesta final entregada en el POST
            super_res_data = {
                'DocumentsIDs': douments,
                'responsibleCode': getCurrentUser(),
                'announcementCode': announcementCode,
                'entityID': getCurrentEntity(),
                'totalAnalysis': totalAnalysis,
                'productsAnalysis': anaylisis_prod,
                'AnalysisDate': datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
            }

            #Se crea el registro histórico de análisis
            # Save in collection MongoDB
            db = client.get_database(__collection__)
            collection = db.BidRiggingDetectionAnalysis
            collection.insert_one(super_res_data)
            #Envío del email
        except:
            #Se limpia el historico
            return jsonify(status_code=500, message='Error to analize document!')
        return jsonify(status_code=200, success=True, message='Return info match', data=super_res_data)
