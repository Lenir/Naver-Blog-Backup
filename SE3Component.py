from bs4 import BeautifulSoup
from urllib import request
import urllib
import re


class SE3Component:
    # SE3Component is class that based on str, found on soup(= HTML TAG)
    def __init__(self, se3component):
        self.component = str(se3component)

    def handleContentTags(self, crawler):
        self.component = "\n" + self.component
        if self.isParagraphComponent():
            print("TEXT", end=" ")
        elif self.isOutGoingLinkComponent():
            print("LINK", end=' ')
            # TODO : implement backup link block
        elif self.isImageComponent():
            print("IMAGE", end=' ')
            imgUrl = self.getImageUrlInArea()
            imgSaveName = crawler.getSaveImageName(imgUrl)
            self.saveImageInArea(crawler.backupDir, imgSaveName)
            print(": " + imgSaveName, end=', ')
            self.replaceImgSrcTag(imgSaveName)
            crawler.imageCount += 1
        elif self.isMapComponent():
            print("MAP", end=' ')
        elif self.isCodeComponent():
            print("CODE", end=' ')
            # TODO : implement code segment block


    def saveImageInArea(self, backupDir, imgSaveName):
        if self.isImageComponent():
            imageUrl = self.getImageUrlInArea()
            request.urlretrieve(urllib.request.quote(imageUrl.encode('utf-8'), ':?=/'), "./" + backupDir + "/" + imgSaveName)

    def getImageUrlInArea(self):
        imgSrcTag = re.search("src=\".*(png|jpg|gif)?type=.[0-9]*", self.component).group()
        imgUrl = imgSrcTag[5:]
        return imgUrl

    def replaceImgSrcTag(self, imgSaveName):
        self.component = re.sub("src=\".*(png|jpg|gif)?type=.[0-9]*\"", "src=\"" + imgSaveName + "\"", self.component)

    def isParagraphComponent(self):
        if "se_component se_paragraph" in str(self.component):
            return True
        else:
            return False

    def isOutGoingLinkComponent(self):
        if "se_component se_oglink" in str(self.component):
            return True
        else:
            return False

    def isImageComponent(self):
        if "se_component se_image" in str(self.component):
            return True
        else:
            return False

    def isCodeComponent(self):
        if "se_component se_code" in str(self.component):
            return True
        else:
            return False

    def isMapComponent(self):
        if "se_component se_map" in str(self.component):
            return True
        else:
            return False

    def handleAlignTags(self):
        if self.isCenterAlignedArea():
            self.addCenterAlignTag()
        elif self.isRightAlignedArea():
            self.addRightAlignTag()

    def isCenterAlignedArea(self):
        if "se_align-center" in str(self.component):
            return True
        else:
            return False

    def isRightAlignedArea(self):
        if "se_align-right" in str(self.component):
            return True
        else:
            return False

    def addCenterAlignTag(self):
        self.component = "\n<center>\n" + self.component + "\n</center>\n"

    def addRightAlignTag(self):
        self.component = "\n<div align=\"right\">\n" + self.component + "\n</div>\n"

    def __str__(self):
        return self.component