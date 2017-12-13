from bs4 import BeautifulSoup
import requests
import re

class NaverBlogCrawler:
    def __init__(self, url):
        self.url = url
        self.postFrameUrl = self.getPostFrameUrl()

    def isSmartEditor3Posting(self, postFrameUrl):
        pass

    def getPostFrameUrl(self):
        postHtmlSource = requests.get(self.url).text
        postSoup = BeautifulSoup(postHtmlSource, "html5lib")

        mainFrameTag = postSoup.find('frame', {'id': 'mainFrame'})
        mainFrameAttr = str(mainFrameTag).split(' ')

        postUrlSuffix = ""
        for attribute in mainFrameAttr:
            if attribute.startswith("src="):
                postUrlSuffix = str(attribute)[5:len(attribute) - 3]

        postUrlSuffix = postUrlSuffix.replace("amp;", "")
        postFrameUrl = "https://blog.naver.com" + postUrlSuffix

        return postFrameUrl

    def getPostEditAreas(self):
        if self.postFrameUrl is None:
            raise InvalidUrl
        else:
            postBodyHttpResponse = requests.get(self.postFrameUrl).text
            postBodySoup = BeautifulSoup(postBodyHttpResponse, "html5lib")
            editAreas = postBodySoup.find_all('div',{'class':'se_editArea'})
            return editAreas

    def isTextEditArea(self, editArea):
        strEditArea = str(editArea)
        if "se_textView" in strEditArea:
            return True
        else:
            return False

class InvalidUrl(Exception):
    pass