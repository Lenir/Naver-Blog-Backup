from bs4 import BeautifulSoup
import requests
from urllib import request
import urllib


class SE3EditArea:
    # EditArea is class that based on str, found on soup(= HTML TAG)
    def __init__(self, editArea):
        self.area = str(editArea)

    def handleContentTags(self, crawler):
        self.area = "\n" + self.area
        if self.isTextEditArea():
            print("TEXT", end=", ")
        elif self.isLinkEditArea():
            print("LINK", end=' ')
            # TODO : implement backup link block
            pass
        elif self.isImageEditArea():
            print("IMAGE", end=' ')
            imgUrl = self.getImageUrlInArea()
            imgSaveName = crawler.getSaveImageName(imgUrl)
            self.saveImageInArea(crawler.backupDir, imgSaveName)
            print(": " + imgSaveName, end=', ')
            self.replaceImgSrcTag(imgSaveName)
            crawler.imageCount += 1
        elif self.isCodeEditArea():
            print("CODE", end=', ')
            # TODO : implement code segment block


    def saveImageInArea(self, backupDir, imgSaveName):
        if self.isImageEditArea():
            imageUrl = self.getImageUrlInArea()
            request.urlretrieve(urllib.request.quote(imageUrl.encode('utf-8'), ':?=/'), "./" + backupDir + "/" + imgSaveName)

    def getImageUrlInArea(self):
        imgSrcTag = re.search("src=\".*(png|jpg|gif)?type=.[0-9]*", self.area).group()
        imgUrl = imgSrcTag[5:]
        return imgUrl

    def replaceImgSrcTag(self, imgSaveName):
        self.area = re.sub("src=\".*(png|jpg|gif)?type=.[0-9]*\"", "src=\"" + imgSaveName + "\"", self.area)

    def isTextEditArea(self):
        if "se_component se_paragraph" in str(self.area):
            return True
        else:
            return False

    def isLinkEditArea(self):
        if "se_component se_oglink" in str(self.area):
            return True
        else:
            return False

    def isImageEditArea(self):
        if "se_component se_image" in str(self.area):
            return True
        else:
            return False

    def isCodeEditArea(self):
        if "se_component se_code code_stripe" in str(self.area):
            return True
        else:
            return False

    def handleAlignTags(self):
        if self.isCenterAlignedArea():
            self.addCenterAlignTag()
        elif self.isRightAlignedArea():
            self.addRightAlignTag()

    def isCenterAlignedArea(self):
        if "se_align-center" in str(self.area):
            return True
        else:
            return False

    def isRightAlignedArea(self):
        if "se_align-right" in str(self.area):
            return True
        else:
            return False

    def addCenterAlignTag(self):
        self.area = "\n<center>\n" + self.area + "\n</center>\n"

    def addRightAlignTag(self):
        self.area = "\n<div align=\"right\">\n" + self.area + "\n</div>\n"

    def __str__(self):
        return self.area