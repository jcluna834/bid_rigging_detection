__author__ = "Julio Luna"
__email__ = "jcluna834@gmail.com"

from service.base import BaseService
from model import Document
from math import ceil
from sqlalchemy.sql import text
from settings import config
from sqlalchemy.sql.expression import bindparam

class BidRiggingDAO(BaseService):

    def get_docs(self, page=1, per_page=10, all=False):
        """
        Fetches documents' list.
        :param page: Current page, defaults to 1
        :param per_page: Number of records per page, defaults to 10
        :return: List of documents
        """

        start, stop = per_page * (page - 1), per_page * page
        query = {'is_deleted': 0}

        doc_queryset = Document.query.filter_by(**query)
        count = doc_queryset.count()
        doc_queryset = doc_queryset.order_by(Document.created_date.desc())
        docs = doc_queryset.all() if all else doc_queryset.slice(start, stop).all()

        return {
            "data": docs,
            "count": count
        }
    
    def get_docs_info(self):
        """
        Fetches documents' list.
        :param page: Current page, defaults to 1
        :param per_page: Number of records per page, defaults to 10
        :return: List of documents
        """

        stmt = text("select d.id as documentId, d.title, d.description as documentDescription, a.id as announcementCode, a.name as announcementName, d.fileName, d.status "
            "from documents d join announcement a on d.announcementCode = a.id "
            "where d.is_deleted = 0 and a.is_deleted = 0 and d.documentType = 2 and d.responsibleCode = :codeUser and a.responsible_code = :codeUser "
            "order by d.title ").\
            bindparams(codeUser=config['USERAUTHID'])
            
        records = self.db.session.execute(stmt).fetchall()
        insertObject = []
        columnNames = [column for column in self.db.session.execute(stmt).keys()]
        for record in records:
            insertObject.append( dict( zip( columnNames , record ) ) )

        return {
            "data": insertObject,
            "count": len(records)
        }

    def get_doc(self, documentId):
        """
        get especific document' .
        :param id: Document id
        :return: List of documents
        """
        query = {'is_deleted': 0, 'id':documentId}
        doc_queryset = Document.query.filter_by(**query)
        docs = doc_queryset.one()
        return docs.to_dict_es()

    def create_doc(self, content, title, fileName, description='', responsibleCode='', announcementCode='', documentType=2):
        """
        Creates an document.
        :param data: document's properties as json.
        :return:
        """
        try:
            doc = Document(content=content, title=title, 
                description=description, 
                responsibleCode=responsibleCode, announcementCode=announcementCode, 
                fileName=fileName, status=1, documentType=documentType)
            
            self.db.session.add(doc)
            self.db.session.commit()
        except Exception as e:
            print(e)
        return doc
