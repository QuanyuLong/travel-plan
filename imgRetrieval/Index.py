#encoding: utf-8
import color_descriptor
import structure_descriptor
import glob
import cv2
#引入color_descriptor和structure_descriptor。用于解析图片库图像，获得色彩空间特征向量和构图空间特征向量。
#用argparse设置命令行参数。参数包括图片库路径、色彩空间特征索引表路径、构图空间特征索引表路径。
#用glob获得图片库路径。
#生成索引表文本并写入csv文件。
#可采用如下命令行形式启动驱动程序。


def index(dataset,colorindex,structureindex):
    """
    dataset: Path to the directory that contains the images to be indexed
    colorindex: Path to where the computed color index will be stored
    structureindex: Path to where the computed structure index will be stored
    """
    
    idealBins = (8, 12, 3)
    colorDesriptor = color_descriptor.ColorDescriptor(idealBins)

    output = open(colorindex, "w")

    for imagePath in glob.glob(dataset + "/*.jpg"):
        try:
            print 'adding(color): '+ imagePath
            imageName = imagePath[imagePath.rfind("/") + 1 : ]
            image = cv2.imread(imagePath)
            features = colorDesriptor.describe(image)
            # write features to file
            features = [str(feature).replace("\n", "") for feature in features]
            output.write("%s,%s\n" % (imageName, ",".join(features)))
        except Exception,e:
            print 'oops'
            continue
    # close index file
    output.close()

    idealDimension = (16, 16)
    structureDescriptor = structure_descriptor.StructureDescriptor(idealDimension)

    output = open(structureindex, "w")

    for imagePath in glob.glob("dataset" + "/*.jpg"):
        try:
            
            print 'adding(structure): ' + imagePath
            imageName = imagePath[imagePath.rfind("/") + 1 : ]
            image = cv2.imread(imagePath)
            structures = structureDescriptor.describe(image)
            # write structures to file
            structures = [str(structure).replace("\n", "") for structure in structures]
            output.write("%s,%s\n" % (imageName, ",".join(structures)))
        except Exception,e:
            continue
    # close index file
    output.close()
    
if __name__ == '__main__':
    index('dataset', 'colorindex', 'structureindex')

