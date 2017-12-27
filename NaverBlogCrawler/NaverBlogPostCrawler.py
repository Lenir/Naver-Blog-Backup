from NaverBlogCrawler import SE2PostViewArea as se2
from NaverBlogCrawler import SE3Component as se3
from bs4 import BeautifulSoup
import requests
from urllib import request, error
import urllib
import os
import re
from datetime import datetime, timedelta

class NaverBlogPostCrawler:
    def __init__(self, url, isDevMode= False):
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
        self.isDevMode = isDevMode

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

        naverBlogUrlRegex = re.compile('http://blog\.naver\.com/.*\?')
        naverBlogUrl = re.search(naverBlogUrlRegex, naverBlogFrame).group()
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
        if self.isDevMode:
            if self.editorVersion is 3:
                print("SE3Post", end=' ')
            else:
                print("SE2Post", end=' ')

    def getPostDate(self):
        publishDate = ""
        if self.editorVersion is 3:
            publishDate = self.postFrameSoup.find('span', {'class': 'se_publishDate pcol2 fil5'})
        else:
            publishDate = self.postFrameSoup.find('p', {'class': 'date fil5 pcol2 _postAddDate'})

        publishDate = str(publishDate)
        if self.isRelativePostDate(publishDate):
            publishDate = self.getRelativePostDate(publishDate)
        else:
            publishDateRegExpr = "20[0-9][0-9]\. [0-9]+\. [0-9]+\. [0-9]+:[0-9]+"
            publishDate = re.search(publishDateRegExpr, publishDate).group()
        return publishDate

    def isRelativePostDate(self, postDate):
        if "전" in postDate:
            return True
        else:
            return False

    def getRelativePostDate(self, relativeDate):
        # eg. "방금 전", "3분전", "10시간 전"...
        curTime = datetime.now()
        if relativeDate == "방금 전":
            pass
        elif "분 전" in relativeDate:
            elapsedMin = re.search("[0-9]+", relativeDate).group()
            elapsedMin = int(elapsedMin)
            curTime = curTime - timedelta(minutes= elapsedMin)
        elif "시간 전" in relativeDate:
            elapsedHour = re.search("[0-9]+", relativeDate).group()
            elapsedHour = int(elapsedHour)
            curTime = curTime - timedelta(hours= elapsedHour)
        curTime = str(curTime)
        timeRegex = re.compile("[0-9]+-[0-9]+-[0-9]+ [0-9]+:[0-9]+")
        curTime = timeRegex.search(curTime).group()
        return curTime

    def run(self):
        self.postSetup()
        if self.isDevMode:
            print(self.postTitle, end=' ')
        self.writeStyleToFile()
        self.writeTitleAreaToFile()
        self.writeHtmlToFile()
        self.backupFile.close()
        if self.isDevMode:
            print()

    def writeStyleToFile(self):
        styleTag = "<link rel=\"stylesheet\" type=\"text/css\" href=\"../../blogstyle.css\" />"
        self.backupFile.write(styleTag)

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

    def getSE3Components(self):
        components = []
        if self.postFrameUrl is None:
            raise InvalidUrl
        else:
            paragraphDivClassName = 'se_paragraph'
            imgDivClassName = 'se_image'
            linkDivClassName = 'se_oglink'
            codeDivClassName = 'se_code'
            mapDivClassName = 'se_map'
            rawComponents = self.postFrameSoup.find_all('div', {'class': {paragraphDivClassName,
                                                                         imgDivClassName,
                                                                         codeDivClassName,
                                                                         linkDivClassName,
                                                                         mapDivClassName}})
            for component in rawComponents:
                components.append(se3.SE3Component(component, self.isDevMode))
            return components

    def getSE2PostViewArea(self):
        rawPostViewArea = self.postFrameSoup.find('div', {'id': 'postViewArea'})
        postViewArea = se2.SE2PostViewArea(rawPostViewArea, self.isDevMode)
        return postViewArea

    def writeHtmlToFile(self):
        if self.editorVersion is 3:
            components = self.getSE3Components()
            if self.isDevMode:
                print("[", end=' ')
            for component in components:
                component.handleContentTags(self)
                component.handleAlignTags()
                self.backupFile.write(str(component))
            if self.isDevMode:
                print("]", end=' ')
        elif self.editorVersion is 2:
            postViewArea = self.getSE2PostViewArea()
            postViewArea.handleParagraphs(self)
            postViewArea.writeSE2PostToFile(self)
        self.prepareCloseHtml()
        self.backupFile.close()

    def setupHtml(self):
        headers = \
            "<html>\n" \
            "    <head>\n" \
            "        <meta http-equiv=\"content-type\" content=\"text/html;charset=UTF-8\"/>\n" \
            "        <title>{}</title>\n" \
            "    </head>\n" \
            "    <body>\n".format(self.postTitle)
        self.backupFile.write(headers)

    def prepareCloseHtml(self):
        tagClosers = \
            "\n" \
            "    </body>\n" \
            "</html>"
        self.backupFile.write(tagClosers)

    def saveImage(self, imageUrl):
        saveLoc = self.backupDir
        saveName = self.getSaveImageName(imageUrl)
        request.urlretrieve(imageUrl, "./" + saveLoc + "/" + str(saveName))

    def getSaveImageName(self, imageUrl):
        return str(self.imageCount) + "." + re.search('(png|jpg|gif)', imageUrl, re.IGNORECASE).group()


class InvalidUrl(Exception):
    pass

