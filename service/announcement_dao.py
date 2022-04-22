__author__ = "Julio Luna"
__email__ = "jcluna834@gmail.com"

from service.base import BaseService
from model import Announcement
from math import ceil
from settings import config

class AnnouncementDAO(BaseService):

    def getCurrentUser(self):
        return config['USERAUTHID']

    def getCurrentEntity(self):
        return config['ENTITYID']

    def get_announcements(self, page=1, per_page=10, all=False):
        """
        Fetches announcements' list.
        :param page: Current page, defaults to 1
        :param per_page: Number of records per page, defaults to 10
        :return: List of announcements
        """
        start, stop = per_page * (page - 1), per_page * page
        query = {'is_deleted': 0, 'responsible_code': self.getCurrentUser(), 'entity_code': self.getCurrentEntity()}

        doc_queryset = Announcement.query.filter_by(**query)
        count = doc_queryset.count()
        doc_queryset = doc_queryset.order_by(Announcement.created_date.desc())
        docs = doc_queryset.all() if all else doc_queryset.slice(start, stop).all()
        
        return {
            "data": docs,
            "count": count
        }

    def get_announcement(self, announcementId):
        """
        get especific document' .
        :param id: Document id
        :return: List of documents
        """
        query = {'is_deleted': 0, 'id':announcementId}
        doc_queryset = Announcement.query.filter_by(**query)
        docs = doc_queryset.one()
        return docs.to_dict()
