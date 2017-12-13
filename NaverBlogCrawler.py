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
        self.postSetup()

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
    # eg. 221156999402[자료구조] 트라이(Trie)
    def getBackupDirName(self):
        dirName = "posts/"
        return dirName + self.postNumber + self.postTitle

    def getPostTitle(self):
        titleTag = self.postFrameSoup.find('title')
        title = re.sub("<title>", '', str(titleTag))
        title = re.sub(" : 네이버 블로그</title>", '', title)
        return title

    def getPostEditAreas(self):
        if self.postFrameUrl is None:
            raise InvalidUrl
        else:
            editAreas = self.postFrameSoup.find_all('div',{'class':'se_editArea'})
            return editAreas

    def isTextEditArea(self, editArea):
        strEditArea = str(editArea)
        if "se_textView" in strEditArea:
            return True
        else:
            return False

    def saveImage(self, imageUrl, saveLoc):
        saveName = self.getSaveImageName(imageUrl)
        request.urlretrieve(imageUrl, saveLoc + saveName)

    def getSaveImageName(self, imageUrl):
        fname = re.search('net/.*(PNG|JPEG|GIF)', imageUrl).group()
        fname = re.sub('[/]', '', fname)
        return fname[3:] #for delete 'net'

class InvalidUrl(Exception):
    pass