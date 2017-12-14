from bs4 import BeautifulSoup
import requests
from urllib import request
import os
import re

class NaverBlogCrawler:
    def __init__(self, url):
        self.url = url
        self.postFrameUrl = ""
        self.postTitle = ""
        self.postNumber = ""
        self.postSoup = None
        self.postFrameSoup = None
        self.backupDir = ""
        self.backupFile = None
        self.imageCount = 0

    def isSmartEditor3Posting(self, postFrameUrl):
        pass

    def postSetup(self):
        postHtmlSource = requests.get(self.url).text
        self.postSoup = BeautifulSoup(postHtmlSource, "html5lib")
        self.postFrameUrl = self.getPostFrameUrl()
        self.postNumber = self.getPostNumber()


        postFrameHttpResponse = requests.get(self.postFrameUrl).text
        self.postFrameSoup = BeautifulSoup(postFrameHttpResponse, "html5lib")
        self.postTitle = self.getPostTitle()

        self.backupDir = self.getBackupDirName()

        self.makeBackupDir()
        self.backupFile = open(self.backupDir+"/post.html", 'w', encoding='utf-8')
        self.setupHtml()
        del self.postSoup

    def run(self):
        self.postSetup()
        self.writeTitleAreaToFile()
        self.writeAreasToFile()
        self.backupFile.close()

    def getPostFrameUrl(self):
        mainFrameTag = self.postSoup.find('frame', {'id': 'mainFrame'})
        mainFrameAttr = str(mainFrameTag).split(' ')

        postUrlSuffix = ""
        for attribute in mainFrameAttr:
            if attribute.startswith("src="):
                postUrlSuffix = str(attribute)[5:len(attribute) - 3]

        postUrlSuffix = postUrlSuffix.replace("amp;", "")
        postFrameUrl = "https://blog.naver.com" + postUrlSuffix

        return postFrameUrl

    def getPostNumber(self):
        postNum = re.sub(".*naver.com/.*/", '', self.url)
        return postNum

    def makeBackupDir(self):
        os.makedirs(self.backupDir, exist_ok=True)

    # post backup will save in ./posts/{postnumber+posttitle}
    # eg. ./posts/221156999402[자료구조] 트라이(Trie)/
    def getBackupDirName(self):
        dirName = "posts/"
        return dirName + self.postNumber + self.postTitle

    def writeTitleAreaToFile(self):
        titleTag = self.postFrameSoup.find('div', {'class' : 'se_editView se_title'})
        self.backupFile.write(str(titleTag))

    def getPostTitle(self):
        titleTag = self.postFrameSoup.find('title')
        title = re.sub("<title>", '', str(titleTag))
        title = re.sub(" : 네이버 블로그</title>", '', title)
        return title

    def getPostEditAreas(self):
        editAreas = []
        if self.postFrameUrl is None:
            raise InvalidUrl
        else:
            rawEditAreas = self.postFrameSoup.find_all('div', {'class': {'se_component se_paragraph default',
                                                                            'se_component se_image default',
                                                                            'se_component se_oglink default',
                                                                            'se_component se_code code_stripe'}})
            for editArea in rawEditAreas:
                editAreas.append(EditArea(editArea))
            return editAreas

    def writeAreasToFile(self):
        editAreas = self.getPostEditAreas()
        for editArea in editAreas:
            editArea.handleContentTags(self)
            editArea.handleAlignTags()
            self.backupFile.write(str(editArea))
        self.prepareCloseHtml()
        self.backupFile.close()

    def setupHtml(self):
        headers = \
            "<html>\n" \
            "   <head>\n" \
            "       <meta http-equiv=\"content-type\" content=\"text/html;charset=UTF-8\"/>\n" \
            "   </head>\n"
        self.backupFile.write(headers)

    def prepareCloseHtml(self):
        tagClosers = "</html>"
        self.backupFile.write(tagClosers)

    def isTextEditArea(self, editArea):
        if "se_component se_paragraph" in str(editArea):
            return True
        else:
            return False

    def isLinkEditArea(self, editArea):
        if "se_component se_oglink" in str(editArea):
            return True
        else:
            return False

    def isImageEditArea(self, editArea):
        if "se_component se_image" in str(editArea):
            return True
        else:
            return False

    def saveImage(self, imageUrl):
        saveLoc = self.backupDir
        saveName = self.getSaveImageName(imageUrl)
        request.urlretrieve(imageUrl, "./" + saveLoc + "/" + str(saveName))

    def getSaveImageName(self, imageUrl):
        return str(self.imageCount) + "." + re.search('(png|jpg|gif)', imageUrl).group()

class InvalidUrl(Exception):
    pass

class EditArea:
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
            imgSaveName = crawler.getSaveImageName(self.getImageUrlInArea())
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
            request.urlretrieve(imageUrl, "./" + backupDir + "/" + imgSaveName)

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