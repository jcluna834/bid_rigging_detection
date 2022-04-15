__author__ = "Julio Luna"
__email__ = "jcluna834@gmail.com"

from service.base import BaseService
import numpy as np
import sys

class BidRiggingDetector(BaseService):

    @staticmethod
    def calculateVariationCoeff(totals):
        """
        Calcula el coeficietne de variación dado una lista de totales
        :param totals:
        :return cv:
        """
        return np.std(totals) / np.mean(totals)

    @staticmethod
    def calculateKurtosisCoeff(totals):
        """
        Calcula el kurtosis dado una lista de totales
        :param totals:
        :return kurt:
        """
        no_bids = len(totals)
        mean_bid = np.mean(totals)
        sdev_bid = np.std(totals)
        kurt = 0

        for bid in totals:
            kurt += pow(( (bid - mean_bid) / sdev_bid ), 4)

        kurt = kurt * no_bids * (no_bids + 1) / ((no_bids - 1) * (no_bids - 2) * (no_bids - 3))
        kurt = kurt - 3 * pow((no_bids - 1), 3) / ((no_bids - 2) * no_bids - 3)
        return kurt

    @staticmethod
    def calculatePercentageDifference(totals):
        """
        Calcula la diferencia porcentual dado una lista de totales
        :param totals:
        :return diff_perc:
        """
        min_bid = min(totals)
        second_min_bid = sorted(totals)[1] 
        diff = (second_min_bid - min_bid) / min_bid
        return diff

    @staticmethod
    def calculateRelativeDifference(totals):
        """
        Calcula la diferencia relativa dado una lista de totales
        :param totals:
        :return rel_perc:
        """
        min_bid = min(totals)
        second_min_bid = sorted(totals)[1]
        loser_bids = sorted(totals)[1 : ]
        sdev_bid = np.std(loser_bids)
        diff = (second_min_bid - min_bid) / sdev_bid
        return diff

    @staticmethod
    def calculateNormalizeRelativeDifference(totals):
        """
        Calcula la diferencia relativa dado una lista de totales
        :param totals:
        :return rel_perc:
        """
        no_bids = len(totals)
        min_bid = min(totals)
        second_min_bid = sorted(totals)[1]
        
        totals = sorted(totals)
        normd = 0
        for i in range(len(totals) - 1):
            normd += totals[i + 1] - totals[i]
        
        normd = sys.float_info.min if (normd == 0) else normd 
        normd = (no_bids - 1) * (second_min_bid - min_bid) / normd
        return normd

    def calculateMeasures(self, totals):
        cv = self.calculateVariationCoeff(totals)
        kurtosis = self.calculateKurtosisCoeff(totals)
        diffPerc = self.calculatePercentageDifference(totals)
        diffRel = self.calculateRelativeDifference(totals)
        normDiffRel = self.calculateNormalizeRelativeDifference(totals)
        response = {
            "VariationCoeff" : cv,
            "KurtosisCoeff" : kurtosis,
            "PercentageDifference" : diffPerc,
            "RelativeDifference" : diffRel,
            "NormalizeRelativeDifference" : normDiffRel,
        }
        return response