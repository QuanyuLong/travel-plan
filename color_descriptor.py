#encoding: utf-8
import cv2
import numpy

#颜色空间特征提取器ColorDescriptor

class ColorDescriptor:
    __slot__ = ["bins"]
    def __init__(self, bins):
        self.bins = bins
    def getHistogram(self, image, mask, isCenter):
        """生成图像的色彩特征分布直方图。
        image为待处理图像，
        mask为图像处理区域的掩模，
        isCenter判断是否为图像中心，
        从而有效地对色彩特征向量做加权处理"""
        # get histogram
        imageHistogram = cv2.calcHist([image], [0, 1, 2], mask, self.bins, [0, 180, 0, 256, 0, 256])
        # normalize
        imageHistogram = cv2.normalize(imageHistogram, imageHistogram).flatten()
        if isCenter:
            weight = 5.0
            for index in xrange(len(imageHistogram)):
                imageHistogram[index] *= weight
        return imageHistogram
        
    def describe(self, image):
        """
        将图像从BGR色彩空间转为HSV色彩空间（此处应注意OpenCV读入图像的色彩空间为BGR而非RGB）。
        生成左上、右上、左下、右下、中心部分的掩模。中心部分掩模的形状为椭圆形。
        这样能够有效区分中心部分和边缘部分，从而在getHistogram()方法中对不同部位的色彩特征做加权处理。
        """
        image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        features = []
        # get dimension and center
        height, width = image.shape[0], image.shape[1]
        centerX, centerY = int(width * 0.5), int(height * 0.5)
        # initialize mask dimension
        segments = [(0, centerX, 0, centerY), (0, centerX, centerY, height), (centerX, width, 0, centerY), (centerX, width, centerY, height)]
        # initialize center part
        axesX, axesY = int(width * 0.75) / 2, int (height * 0.75) / 2
        ellipseMask = numpy.zeros([height, width], dtype="uint8")
        cv2.ellipse(ellipseMask, (centerX, centerY), (axesX, axesY), 0, 0, 360, 255, -1)
        # initialize corner part
        for startX, endX, startY, endY in segments:
            cornerMask = numpy.zeros([height, width], dtype="uint8")
            cv2.rectangle(cornerMask, (startX, startY), (endX, endY), 255, -1)
            cornerMask = cv2.subtract(cornerMask, ellipseMask)
            # get histogram of corner part
            imageHistogram = self.getHistogram(image, cornerMask, False)
            features.append(imageHistogram)
        # get histogram of center part
        imageHistogram = self.getHistogram(image, ellipseMask, True)
        features.append(imageHistogram)
        # return
        return features


if __name__ == '__main__':
    idealBins = (8, 12, 3)
    colorDesriptor = ColorDescriptor(idealBins)
    img = cv2.imread('target.jpg',cv2.IMREAD_COLOR)
    features = colorDesriptor.describe(img)
    print str(features[0]).replace("\n", "")

