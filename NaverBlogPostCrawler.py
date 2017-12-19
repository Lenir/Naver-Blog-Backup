from SE3EditArea import *
from SE2PostViewArea import *

from bs4 import BeautifulSoup
import requests
from urllib import request, error
import urllib
import os
import re

class NaverBlogPostCrawler:
    def __init__(self, url):
        self.url = url
        if self.isforeignURL():
            self.url = self.getNaverBlogUrl()
        self.postFrameUrl = ""
        self.editorVersion = None
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
        naverBlogUrl = re.search('http://blog\.naver\.com/.*\?', naverBlogFrame).group()
        return naverBlogUrl

    def getEditorVersion(self):
        SE3Tag = self.postFrameSoup.find('p', {'class': 'write_by_smarteditor3'})
        if SE3Tag is None:
            return 2
        else:
            return 3

    def postSetup(self):
        postHtmlSource = requests.get(self.url).text
        postSoup = BeautifulSoup(postHtmlSource, "html5lib")
        self.postFrameUrl = self.getPostFrameUrl(postSoup)

        postFrameHttpResponse = requests.get(self.postFrameUrl).text
        self.postFrameSoup = BeautifulSoup(postFrameHttpResponse, "html5lib")

        self.editorVersion = self.getEditorVersion()

        self.postTitle = self.getPostTitle()
        self.postDate = self.getPostDate()
        self.backupDir = self.getBackupDirName()

        self.makeBackupDir()
        self.backupFile = open(self.backupDir + "/post.html", 'w', encoding='utf-8')
        self.setupHtml()

        if self.editorVersion is 3:
            pass
        else:
            print("SE2Post", end=' ')

    def getPostDate(self):
        # TODO : if publishDate is not like 2017. 12. 10... debug.
        publishDate = ""

        if self.editorVersion is 3:
            publishDate = self.postFrameSoup.find('span', {'class': 'se_publishDate pcol2 fil5'})
        else:
            publishDate = self.postFrameSoup.find('p', {'class': 'date fil5 pcol2 _postAddDate'})

        publishDate = str(publishDate)
        publishDateRegExpr = "20[0-9][0-9]\. [0-9]+\. [0-9]+\. [0-9]+:[0-9]+"
        publishDate = re.search(publishDateRegExpr, publishDate).group()

        return publishDate

    def run(self):
        self.postSetup()
        print(self.postTitle)
        self.writeTitleAreaToFile()
        self.writeAreasToFile()
        self.backupFile.close()
        print()

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
        processedDate = self.removeCharCannotUseDirName(self.postDate)
        processedTitle = "[" + self.removeCharCannotUseDirName(self.postTitle) + "]"
        dirName = "posts/" + processedDate + " " + processedTitle
        return dirName

    def writeTitleAreaToFile(self):
        titleTag = self.getTitleTag()
        self.backupFile.write(str(titleTag))

    def removeCharCannotUseDirName(self, dirName):
        windowsDir = re.compile('[\?:|<|>|\||\*|\"\/]') # Special Chars that cannot use in Windows' Directory Name
        fixedDirName = windowsDir.sub('', dirName)
        return fixedDirName

    def getTitleTag(self):
        if self.editorVersion is 3:
            titleTag = self.postFrameSoup.find('div', {'class': 'se_editView se_title'})
        else:
            titleTag = self.postFrameSoup.find('span', {'class': 'pcol1 itemSubjectBoldfont'})
        return titleTag

    def getPostTitle(self):
        titleTag = self.postFrameSoup.find('title')
        titleTag = str(titleTag)
        titleTag = re.sub("<title>", '', titleTag)
        titleTag = re.sub(" : 네이버 블로그</title>", '', titleTag)
        return titleTag

    def getSE3PostEditAreas(self):
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
                editAreas.append(SE3EditArea(editArea))
            return editAreas

    def getSE2PostViewArea(self):
        rawPostViewArea = self.postFrameSoup.find('div', {'id': 'postViewArea'})
        postViewArea = SE2PostViewArea(rawPostViewArea)
        return postViewArea

    def writeAreasToFile(self):
        if self.editorVersion is 3:
            editAreas = self.getSE3PostEditAreas()
            for editArea in editAreas:
                editArea.handleContentTags(self)
                editArea.handleAlignTags()
                self.backupFile.write(str(editArea))
        elif self.editorVersion is 2:
            postViewArea = self.getSE2PostViewArea()
            postViewArea.handleParagraphs(self)
            postViewArea.writeSE2PostToFile(self)
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
        return str(self.imageCount) + "." + re.search('(png|jpg|gif)', imageUrl, re.IGNORECASE).group()


class InvalidUrl(Exception):
    pass


if __name__ == "__main__":
    # crawler = NaverBlogPostCrawler("http://blog.kgitbank.co.kr/221123110233")
    # crawler.run()
    # print(crawler.postDate)

    chineseCharPost = "http://blog.naver.com/1net1/30088908014"
    doubleQuotedImgPost = "https://blog.naver.com/1net1/30082417095"
    recentPost = "http://blog.naver.com/1net1/221163927928"

    crawler = NaverBlogPostCrawler(doubleQuotedImgPost)
    crawler.run()

