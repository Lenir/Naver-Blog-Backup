from bs4 import BeautifulSoup
import requests
from urllib import request
import os
import re

class NaverBlogPostCrawler:
    def __init__(self, url):
        self.url = url
        if self.isforeignURL():
            self.url = self.getNaverBlogUrl()
        self.postFrameUrl = ""
        self.postTitle = ""
        self.postFrameSoup = None
        self.backupDir = ""
        self.backupFile = None
        self.imageCount = 0
        self.postDate = None

    def isforeignURL(self):
        if "blog.naver.com" in self.url:
            return False
        else:
            return True

    def getNaverBlogUrl(self):
        foreignSource = requests.get(self.url).text
        foreignSoup = BeautifulSoup(foreignSource, "html5lib")
        naverBlogFrame = foreignSoup.find('frame', {'id': 'screenFrame'})
        naverBlogFrame = str(naverBlogFrame)
        print(naverBlogFrame)
        naverBlogUrl = re.search('http://blog\.naver\.com/.*\?', naverBlogFrame).group()
        return naverBlogUrl

    def isSmartEditor3Posting(self, postFrameUrl):
        # TODO : if posting is SE3, do current way, is not, impelement new methods.
        pass

    def postSetup(self):
        postHtmlSource = requests.get(self.url).text
        postSoup = BeautifulSoup(postHtmlSource, "html5lib")
        self.postFrameUrl = self.getPostFrameUrl(postSoup)
        print(self.postFrameUrl)

        postFrameHttpResponse = requests.get(self.postFrameUrl).text
        self.postFrameSoup = BeautifulSoup(postFrameHttpResponse, "html5lib")
        self.postTitle = self.getPostTitle()
        self.postDate = self.getPostDate()

        self.backupDir = self.getBackupDirName()

        self.makeBackupDir()
        self.backupFile = open(self.backupDir+"/post.html", 'w', encoding='utf-8')
        self.setupHtml()

    def getPostDate(self):
        # TODO : if publishDate is not like 2017. 12. 10... debug.
        publishDate = self.postFrameSoup.find('span', {'class': 'se_publishDate pcol2 fil5'})
        print(publishDate)
        publishDate = str(publishDate)
        publishDateRegExpr = "20[0-9][0-9]\. [0-9]+\. [0-9]+\. [0-9]+:[0-9]+"
        publishDate = re.search(publishDateRegExpr, publishDate).group()

        return publishDate

    def run(self):
        self.postSetup()
        self.writeTitleAreaToFile()
        self.writeAreasToFile()
        self.backupFile.close()

    def getPostFrameUrl(self, postSoup):
        mainFrameTag = postSoup.find('frame', {'id': 'mainFrame'})
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

    # post backup will save in ./posts/{postDate + " " + postTitle}/...
    def getBackupDirName(self):
        dirName = "posts/"
        return dirName + self.postDate + " " + self.postTitle

    def writeTitleAreaToFile(self):
        titleTag = self.postFrameSoup.find('div', {'class' : 'se_editView se_title'})
        self.backupFile.write(str(titleTag))

    def getPostTitle(self):
        titleTag = self.postFrameSoup.find('title')
        titleTag = str(titleTag)
        titleTag = re.sub("<title>", '', titleTag)
        titleTag = re.sub(" : 네이버 블로그</title>", '', titleTag)
        return titleTag

    def getPostEditAreas(self):
        editAreas = []
        if self.postFrameUrl is None:
            raise InvalidUrl
        else:
            textViewClassName = 'se_component se_paragraph default'
            imgViewClassName = 'se_component se_image default'
            linkViewClassName = 'se_component se_oglink default'
            codeViewClassName = 'se_component se_code code_stripe'
            rawEditAreas = self.postFrameSoup.find_all('div', {'class': {textViewClassName,
                                                                         imgViewClassName,
                                                                         codeViewClassName,
                                                                         linkViewClassName}})
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
            "       <title>{}</title>\n" \
            "   </head>\n".format(self.postTitle)
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
        print(self.area)

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

if __name__ == "__main__":
    crawler = NaverBlogPostCrawler("http://blog.kgitbank.co.kr/221123110233")
    crawler.run()
    print(crawler.postDate)