#encoding:utf8
import color_descriptor
import structure_descriptor
import searcher
import cv2
import os
import urllib
def searchEngine(colorIndexPath, structureIndexPath, query):
    """
        colorIndexPath: Path to where the computed color index will be stored
        structureIndexPath: Path to where the computed structure index will be stored
        query: 可以是一个图片的路径，也可以是一个图片的url
        当传入图片的url时，会将图片下载到当前工作目录中，形成query.jpg
    """
    idealBins = (8, 12, 3)
    idealDimension = (16, 16)
    colorDescriptor = color_descriptor.ColorDescriptor(idealBins)
    structureDescriptor = structure_descriptor.StructureDescriptor(idealDimension)
    if not os.path.exists(query):
        try:
            downloadpath = os.path.join(os.getcwd(), 'query.jpg')
            urllib.urlretrieve(query, downloadpath)
            queryImage = cv2.imread('query.jpg')
        except Exception,e:
            print str(e)
            return None
    else:
        queryImage = cv2.imread(query)
    queryFeatures = colorDescriptor.describe(queryImage)
    queryStructures = structureDescriptor.describe(queryImage)

    imageSearcher = searcher.Searcher(colorIndexPath, structureIndexPath)
    searchResults = imageSearcher.search(queryFeatures, queryStructures,1)#返回3个最优解
    for imageName, score in searchResults:
        print imageName
        return imageName
    #print searchResults
    #return searchResults

if __name__ == '__main__':
    colorIndexPath = 'colorindex'
    structureIndexPath = 'structureindex'
    query = 'test_5.jpg'
    searchEngine(colorIndexPath, structureIndexPath, query)

