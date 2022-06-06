__author__ = "Julio Luna"
__email__ = "jcluna834@gmail.com"

from dbm import dumb
from math import prod
from controller.base import BaseController
from flask import jsonify, request
from pymongo import MongoClient
from settings import app, config
from util.injector import inject
from service.bid_detector import BidRiggingDetector
from datetime import datetime
from bson.objectid import ObjectId
from service.announcement_dao import AnnouncementDAO
import json 
from bson.json_util import dumps

client = MongoClient('localhost:27017')
__collection__ = 'PlagiarismDetection'

def getCurrentUser():
    return config['USERAUTHID']

def getCurrentEntity():
    return config['ENTITYID']
class BidRiggingDetection(BaseController):
    bid_detector: BidRiggingDetector = inject(BidRiggingDetector)
    announcement_dao: AnnouncementDAO = inject(AnnouncementDAO)

    def __init__(self):
        self.events = []

    
    @app.route("/api/v1/bidrigging/detect/getReportsBidRiggingByAnnouncement/<announcementCode>", methods=['GET'])
    def getReportsSimilarityByDocumentId(announcementCode):
        bidRiggingController = BidRiggingDetection()
        # Se obtiene la información del documento
        db = client.get_database(__collection__)
        collection = db.BidRiggingDetectionAnalysis
        responseCollection = collection.find({"responsibleCode": getCurrentUser(), "announcementCode": announcementCode})
        proposals = list(responseCollection)
        return jsonify(status_code=200, message='Reports returned successfully!', data=proposals)

    @app.route("/api/v1/bidrigging/detect/getReport/<id>", methods=['GET'])
    def getReport(id):
        try:
            db = client.get_database(__collection__)
            collection = db.BidRiggingDetectionAnalysis
            responseCollection = collection.find({"_id":ObjectId(id)})
            list_cur = list(responseCollection)
        except:
            #Se limpia el historico
            return jsonify(status_code=500, message='Error to get report!')
        return jsonify(status_code=200, message='Report returned successfully!', data=list_cur)

    @app.route("/api/v1/bidrigging/getAnnouncementInfo/<announcementID>", methods=['GET'])
    def getAnnouncementInfo(announcementID):
        try:
            bidRiggingController = BidRiggingDetection()
            announcement = bidRiggingController.announcement_dao.get_announcement(announcementID)
        except:
            #Se limpia el historico
            return jsonify(status_code=500, message='Error to get announcement!')
        return jsonify(status_code=200, message='Report returned successfully!', data = announcement)
        
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
                    productsDict = {"PROD_ID": product["Identificación"], "PROD_NAME": product["Nombre del producto/servicio"], "PROD_LIST": productsList}
                products.append(productsDict)
            
            anaylisis_prod = []
            for product in products:
                response = bidRiggingController.bid_detector.calculateMeasures(product["PROD_LIST"])
                data = {
                    'PROD_ID': product['PROD_ID'],
                    'PROD_NAME': product['PROD_NAME'],
                    'PROD_LIST': product["PROD_LIST"],
                    'Anaylis': response
                }
                anaylisis_prod.append(data)
            
            #Se calcula la probabilidad de manipulación por documento siguiendo el algoritmo LexRank
            totalsByProducts = []
            for proposal in proposals:
                totalsByProducts.append([products["Total"] for products in proposal["productsInfo"]])

            lexRank = bidRiggingController.bid_detector.calculateLexRank(totalsByProducts)
            anaylisis_docs = []
            i = 0
            for document in douments:
                data = {
                    'docId': document,
                    'probabilityLexRank': round(lexRank[i], 2),
                }
                anaylisis_docs.append(data)
                i += 1

            # Respuesta final entregada en el POST
            super_res_data = {
                'DocumentsIDs': douments,
                'responsibleCode': getCurrentUser(),
                'announcementCode': announcementCode,
                'entityID': getCurrentEntity(),
                'totalAnalysis': totalAnalysis,
                'productsAnalysis': anaylisis_prod,
                'documentsProbabilityLexRank': anaylisis_docs,
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


    @app.route("/api/v1/bidrigging/detect/executeLexRank", methods=['POST'])
    def executeLexRank():
        bidRiggingController = BidRiggingDetection()
        data = request.get_json()
        announcementCode = data['announcementCode']

        # Se obtiene la información del documento
        db = client.get_database(__collection__)
        collection = db.BidRiggingDetection
        responseCollection = collection.find({"responsibleCode": getCurrentUser(), "announcementCode": announcementCode})
        proposals = list(responseCollection)
        totals = []
        for proposal in proposals:
            totals.append([products["Total"] for products in proposal["productsInfo"]])
        
        # Se obtiene el cálculo de LexRank para cada propuesta
        lexRank = bidRiggingController.bid_detector.calculateLexRank(totals)
        douments = [proposal["documentID"] for proposal in proposals]

        anaylisis_docs = []
        i = 0
        for document in douments:
            data = {
                'docId': document,
                'probabilityLexRank': round(lexRank[i], 2),
            }
            anaylisis_docs.append(data)
            i += 1


        return jsonify(status_code=200, success=True, message='Return info match', data=anaylisis_docs)

