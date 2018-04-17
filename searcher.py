#encoding:utf8
import numpy
import csv
import re

#    1.类成员colorIndexPath和structureIndexPath。记录色彩空间特征索引表路径和结构特征索引表路径。
#    2.成员函数solveColorDistance(self, features, queryFeatures, eps = 1e-5)。求features和queryFeatures特征向量的二范数。eps是为了避免除零错误。
#    3.成员函数solveStructureDistance(self, structures, queryStructures, eps = 1e-5)。同样是求特征向量的二范数。eps是为了避免除零错误。需作统一化处理，color和structure特征向量距离相对比例适中，不可过分偏颇。
#    4.成员函数searchByColor(self, queryFeatures)。使用csv模块的reader方法读入索引表数据。采用re的split方法解析数据格式。用字典searchResults存储query图像与库中图像的距离，键为图库内图像名imageName，值为距离distance。
#    5.成员函数transformRawQuery(self, rawQueryStructures)。将未处理的query图像矩阵转为用于匹配的特征向量形式。
#    6.成员函数searchByStructure(self, rawQueryStructures)。类似4。
#    7.成员函数search(self, queryFeatures, rawQueryStructures, limit = 3)。将searchByColor方法和searchByStructure的结果汇总，获得总匹配分值，分值越低代表综合距离越小，匹配程度越高。返回前limit个最佳匹配图像。
class Searcher:
    __slot__ = ["colorIndexPath", "structureIndexPath"]
    
    def __init__(self, colorIndexPath, structureIndexPath):
        self.colorIndexPath, self.structureIndexPath = colorIndexPath, structureIndexPath
        
    def solveColorDistance(self, features, queryFeatures, eps = 1e-5):
        distance = 0.5 * numpy.sum([((a - b) ** 2) / (a + b + eps) for a, b in zip(features, queryFeatures)])
        return distance
        
    def solveStructureDistance(self, structures, queryStructures, eps = 1e-5):
        distance = 0
        normalizeRatio = 5e3
        for index in xrange(len(queryStructures)):
            for subIndex in xrange(len(queryStructures[index])):
                a = structures[index][subIndex]
                b = queryStructures[index][subIndex]
                distance += (a - b) ** 2 / (a + b + eps)
        return distance / normalizeRatio
        
    def searchByColor(self, queryFeatures):
        searchResults = {}
        with open(self.colorIndexPath) as indexFile:
            reader = csv.reader(indexFile)
            for line in reader:
                features = []
                for feature in line[1:]:
                    feature = feature.replace("[", "").replace("]", "")
                    findStartPosition = 0
                    feature = re.split("\s+", feature)
                    rmlist = []
                    for index, strValue in enumerate(feature):
                        if strValue == "":
                            rmlist.append(index)
                    for _ in xrange(len(rmlist)):
                        currentIndex = rmlist[-1]
                        rmlist.pop()
                        del feature[currentIndex]
                    feature = [float(eachValue) for eachValue in feature]
                    features.append(feature)
                distance = self.solveColorDistance(features, queryFeatures)
                searchResults[line[0]] = distance
            indexFile.close()
        # print "feature", sorted(searchResults.iteritems(), key = lambda item: item[1], reverse = False)
        return searchResults
    def transformRawQuery(self, rawQueryStructures):
        queryStructures = []
        for substructure in rawQueryStructures:
            structure = []
            for line in substructure:
                for tripleColor in line:
                    structure.append(float(tripleColor))
            queryStructures.append(structure)
        return queryStructures
    def searchByStructure(self, rawQueryStructures):
        searchResults = {}
        queryStructures = self.transformRawQuery(rawQueryStructures)
        with open(self.structureIndexPath) as indexFile:
            reader = csv.reader(indexFile)
            for line in reader:
                structures = []
                for structure in line[1:]:
                    structure = structure.replace("[", "").replace("]", "")
                    structure = re.split("\s+", structure)
                    if structure[0] == "":
                        structure = structure[1:]
                    structure = [float(eachValue) for eachValue in structure]
                    structures.append(structure)
                distance = self.solveStructureDistance(structures, queryStructures)
                searchResults[line[0]] = distance
            indexFile.close()
        # print "structure", sorted(searchResults.iteritems(), key = lambda item: item[1], reverse = False)
        return searchResults
    def search(self, queryFeatures, rawQueryStructures, limit = 3):
        featureResults = self.searchByColor(queryFeatures)
        structureResults = self.searchByStructure(rawQueryStructures)
        results = {}
        for key, value in featureResults.iteritems():
            results[key] = value + structureResults[key]
        results = sorted(results.iteritems(), key = lambda item: item[1], reverse = False)
        return results[ : limit]
