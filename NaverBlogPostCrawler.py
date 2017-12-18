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


class SE2PostViewArea:
    def __init__(self, postViewArea):
        self.postViewArea = str(postViewArea)
        self.header = self.getHeader()
        self.paragraphs = self.getParagraphs()
        self.footer = self.getFooter()

    def writeSE2PostToFile(self, crawler):
        crawler.backupFile.write("\n")
        crawler.backupFile.write(self.header)
        for p in self.paragraphs:
            crawler.backupFile.write("\n")
            crawler.backupFile.write(p.paragraph)
        crawler.backupFile.write("\n")
        crawler.backupFile.write(self.footer)

    def getHeader(self):
        header = ""
        try:
            header = re.search("<div.*?><p", self.postViewArea, re.DOTALL | re.MULTILINE).group()
            header = header[:len(header)-2]
        except:
            header = " "
        return header

    def getFooter(self):
        footer = re.search("</div>*", self.postViewArea).group()
        return footer

    def getParagraphs(self):
        tags = None
        pTags = re.findall("<p.+?</p>", self.postViewArea, re.DOTALL)
        if len(pTags) < 1:
            divTags = re.findall("<div.+?</div>", self.postViewArea, re.DOTALL)
            tags = divTags
        else:
            tags = pTags
        paragraphs = []
        for tag in tags:
            paragraphs.append(SE2Paragraph(str(tag)))
        return paragraphs

    def handleParagraphs(self, crawler):
        for p in self.paragraphs:
            if p.isImageInParagraph():
                print("IMAGE P", end=' ')
                imgUrl = p.getImageUrlInParagraph()
                imgSaveName = crawler.getSaveImageName(imgUrl)
                p.saveImageInArea(crawler.backupDir, imgSaveName)
                print(": " + imgSaveName, end=', ')
                p.replaceImgSrcTag(imgSaveName)
                crawler.imageCount += 1
            else:
                print("P", end=' ')

class SE2Paragraph:
    def __init__(self, rawParagraph):
        self.paragraph = str(rawParagraph)

    def isImageInParagraph(self):
        if "class=\"_photoImage\"" in self.paragraph:
            return True
        else:
            return False

    def getImageUrlInParagraph(self):
        imgSrcRegularExpr = re.compile("src=\".*?\"")
        imgSrc = imgSrcRegularExpr.search(self.paragraph).group()
        imgUrl = re.sub("src=", '', imgSrc)
        imgUrl = re.sub("\"", '', imgUrl)
        if self.isDoubleQuotedSrc(imgUrl):
            imgUrl = self.getImgUrlInQuotedUrl(imgUrl)
        imgUrl = urllib.request.quote(imgUrl.encode('utf-8'), ':?=/')
        return imgUrl

    def replaceImgSrcTag(self, imgSaveName):
        imgSrcRegularExpr = re.compile("src=\"http.*?\"")
        self.paragraph = imgSrcRegularExpr.sub("src=\"" + imgSaveName + "\"", self.paragraph)

    def saveImageInArea(self, backupDir, imgSaveName):
        if self.isImageInParagraph():
            imageUrl = self.getImageUrlInParagraph()
            try:
                request.urlretrieve(imageUrl, "./" + backupDir + "/" + imgSaveName)
            except urllib.error.HTTPError:
                print("ERROR in image URL")

    def isDoubleQuotedSrc(self, imgUrl):
        if "%22http%3A%2F%2F" in imgUrl:
            return True
        else:
            return False

    def getImgUrlInQuotedUrl(self, quotedUrl):
        print("doubleQ" + quotedUrl)
        quotedImgUrlRegularExpr = re.compile("http\%3A\%2F\%2F.*?(gif|jpg|png)")
        imageUrl = quotedImgUrlRegularExpr.search(quotedUrl).group()
        imageUrl = urllib.request.unquote(imageUrl, encoding='utf-8')
        return imageUrl


if __name__ == "__main__":
    # crawler = NaverBlogPostCrawler("http://blog.kgitbank.co.kr/221123110233")
    # crawler.run()
    # print(crawler.postDate)

    chineseCharPost = "http://blog.naver.com/1net1/30088908014"
    doubleQuotedImgPost = "https://blog.naver.com/1net1/30082417095"
    recentPost = "http://blog.naver.com/1net1/221163927928"

    crawler = NaverBlogPostCrawler(doubleQuotedImgPost)
    crawler.run()

