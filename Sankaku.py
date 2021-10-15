import requests
import mimetypes
import json
import os
import time
import Settings

# region Sankaku stuff
API_URL = "https://capi-v2.sankakucomplex.com/"
HTTP_HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'}

POST_ID = "id"
POST_URL = "file_url"
POST_MIME = "file_type"
# endregion

class Sankaku:
    __session = requests.Session()

    progress = 0
    total = 0
    statusMessage = "idle"

    posts = []

    #region Static
    @staticmethod
    def __getFileType(url): 
        lastQuestionMark = url.rfind('?')
        lastDotBeforeQM = url.rfind('.',0,lastQuestionMark)
        #remove everything before .:?
        return url[lastDotBeforeQM:lastQuestionMark]

    @staticmethod
    def download_post(post, folder):
        if(post[POST_URL] == None):
            print(f"Can't download: {post}")
        r = Sankaku.__session.get(post[POST_URL])
        open(
            os.path.join(folder, str(post[POST_ID])) + Sankaku.__getFileType(post[POST_URL]), 'wb'
        ).write(r.content)
    #endregion

    def get_posts(self):
        page = ""
        self.posts = []
        temp = [0]
        self.output("Downloading pages with posts")
        while(page != None):
            temp = self._getPage(page)
            page = temp['meta']['next']
            self.posts.extend(temp['data'])
        self.output("Pages processed. " + str(len(self.posts)) + " posts found.")
        return self.posts

    def _getPage(self, page = None):
        print("G("+self.tags+"):"+str(page))
        self.output("Getting the page:" + str(page))
        params = {
            'lang':'en',
            'limit':40,
            'tags':self.tags
        }
        if (page != None):
            params['next'] = page
        return json.loads(Sankaku.__session.get(API_URL + 'posts/keyset', params = params).content)


    def __init__(self,tags,folder,print = None):
        self.tags = tags
        self.folder = folder
        self.print = print

    def output(self, string):
        if(callable(self.print)): self.print(string)

    def download(self):
        Sankaku.__session.headers['User-Agent'] = HTTP_HEADERS['User-Agent']
        self.progress = 0
        posts = self.get_posts()
        self.total = len(posts)
        for i in range(self.total):
            self.output("D("+str(i+1)+"/"+str(self.total)+"):"+ str(posts[i][POST_ID]))
            try:
                Sankaku.download_post(posts[i],self.folder)
                self.output("Sleeping for: " + str(Settings.delayBetweenFetches))
                time.sleep(Settings.delayBetweenFetches)
            except BaseException as err:
                self.output("There was some problem here: " + f"Unexpected {err=}")
            self.progress += 1
        self.output("Complete")
