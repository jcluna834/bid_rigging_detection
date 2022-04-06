__author__ = "Julio Luna"
__email__ = "jcluna834@gmail.com"

from service.base import BaseService
from model import Document
from math import ceil
from sqlalchemy.sql import text
from settings import config
from sqlalchemy.sql.expression import bindparam

class PlagiarismDAO(BaseService):

    def yield_docs(self, page=1, per_page=10):
        """
        Yields a list of documents per page.
        :param page:
        :param per_page:
        :return:
        """
        docs = self.get_docs(page=page, per_page=per_page)
        iterations = ceil(docs['count'] / per_page)

        yield docs
        for _page in range(page + 1, iterations + 1):
            docs = self.get_docs(page=_page, per_page=per_page)
            yield docs

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

    def get_doc_info(self, documentId):
        """
        get especific document' .
        :param id: Document id
        :return: List of documents
        """
        query = {'is_deleted': 0, 'id':documentId}
        doc_queryset = Document.query.filter_by(**query)
        docs = doc_queryset.one()
        return docs.to_dict()

    def create_doc(self, content, title, fileName, description='', responsibleCode='', announcementCode=''):
        """
        Creates an document.
        :param data: document's properties as json.
        :return:
        """
        doc = Document(content=content, title=title, 
            description=description, 
            responsibleCode=responsibleCode, announcementCode=announcementCode, 
            fileName=fileName, status=0)
        
        self.db.session.add(doc)
        self.db.session.commit()
        return doc