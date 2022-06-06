__author__ = "Julio Luna"
__email__ = "jcluna834@gmail.com"

from service.base import BaseService
import numpy as np
import sys
from sklearn.metrics import pairwise_distances
from settings import config

class BidRiggingDetector(BaseService):

    @staticmethod
    def minMaxNormalizarion(totals):
        """
        Calcula el min_max dado una lista de totales
        :param totals:
        :return min max:
        """
        totals_norm = []

        min_bid = min(totals)
        max_bid = max(totals)
        for bid in totals:
            new_val = (bid - min_bid) / (max_bid - min_bid)
            totals_norm.append(new_val)

        return totals_norm

    @staticmethod
    def calculateVariationCoeff(totals):
        """
        Calcula el coeficietne de variación dado una lista de totales
        :param totals:
        :return cv:
        """
        return np.std(totals) / np.mean(totals)

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
        #totals_norm = self.minMaxNormalizarion(totals)
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

    @staticmethod
    def powerMethodNumpy(totals):
        max_iteration = config['MAX_ITERATIONS']
        size = len(totals)
        x = np.ones(size)
        a = np.array(totals)

        for i in range(max_iteration):
            x = np.dot(a.transpose(), x)
            lambda_1 = abs(x).max()
            x = x / x.max()

        return x

    @staticmethod
    def powerMethod(totals):
        tolerable_error = 0.001
        size = len(totals)
        a = np.array(totals)
        x = np.ones(size)
        max_iteration = 10
        lambda_old = 1.0
        condition =  True
        step = 1
        while condition:
            x = np.matmul(a.transpose(), x)
            lambda_new = max(abs(x))
            x = x/lambda_new

            print('\nSTEP %d' %(step))
            print('Eigen Value = %0.4f' %(lambda_new))
            print('Eigen Vector: ')
            for i in range(size):
                print('%0.3f\t' % (x[i]))
            
            step = step + 1
            if step > max_iteration:
                print('Not convergent in given maximum iteration!')
                break
            
            # Calculating error
            error = abs(lambda_new - lambda_old)
            print('errror='+ str(error))
            lambda_old = lambda_new
            condition = error > tolerable_error

        return x


    def calculateLexRank(self, totals):
        umbral = config['UMBRAL']
        dampingFactor = config['DAMPINGFACTOR']
        #Se calcula la similitud de cosenos
        #totals_matrix = np.array(totals)
        totals_matrix = totals
        dist_out = 1 - pairwise_distances(totals_matrix, metric="cosine")
        #dist_out = np.round(dist_out, 2)
        #print("info:::", dist_out)

        #Se aplica el umbral 
        #Se normaliza para obtener vector de cambios
        totals_umbral = []
        for cosine_val in dist_out:
            cosine_val = [1 if val > umbral else 0 for val in cosine_val]
            cosine_val = [round(val / sum(cosine_val), 2) for val in cosine_val]
            totals_umbral.append(cosine_val)
        #print (totals_umbral)

        #Convertir la matriz estocástica a irreducible y aperiódica
        size = len(totals_umbral)
        totals_damping = []
        for total_umbral in totals_umbral:
            total_umbral = [round((dampingFactor/size) + (1 - dampingFactor), 2) * val for val in total_umbral]
            totals_damping.append(total_umbral)

        #print (totals_damping)
        #Calculate powerMethod
        #vectorProbability = self.powerMethod(totals_damping) #método mencionado en el algoritmo utilizado
        vectorProbability = self.powerMethodNumpy(totals_damping)
        #print(vectorProbability)
        return vectorProbability