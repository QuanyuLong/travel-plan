#encoding: utf-8
#structure_descriptor.py
import cv2

class StructureDescriptor:
    """1.类成员dimension。将所有图片归一化（降低采样）为dimension所规定的尺寸。由此才能够用于统一的匹配和构图空间特征的生成。
       2.成员函数describe(self, image)。将图像从BGR色彩空间转为HSV色彩空间（此处应注意OpenCV读入图像的色彩空间为BGR而非RGB）。返回HSV色彩空间的矩阵，等待在搜索引擎核心中的下一步处理。
    """
    __slot__ = ["dimension"]
    def __init__(self, dimension):
        self.dimension = dimension
        #dimension是一个二维元组，比如(int(width*0.3), int(height*0.5))表示
        #宽度缩小为原来的0.3倍，长度缩小为原来的0.5倍
    def describe(self, image):
        image = cv2.resize(image, self.dimension, interpolation=cv2.INTER_CUBIC)
        #INTER_CUBIC - 基于4x4像素邻域的3次插值法
        #image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        return image
        
if __name__ == '__main__':
    idealDimension = (16, 16)
    structureDescriptor = StructureDescriptor(idealDimension)
    img = cv2.imread('target.jpg',cv2.IMREAD_COLOR)
    structures = structureDescriptor.describe(img)
    #structures = [str(structure).replace("\n", "") for structure in structures]
    print structures[0][0]
