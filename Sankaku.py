import urllib.request
import mimetypes
import json
import Settings

class Sankaku:
    progress = 0
    total = 0
    statusMessage = "idle"

    posts = []

    

    #region Static
    #region Helpers
    @staticmethod
    def __getUrlJsonToObject(url):
        req = urllib.request.Request(
            url, 
            data=None, 
            headers= Settings.HTTP_HEADERS
        )
        return json.loads(urllib.request.urlopen(req).read().decode('utf-8'))

    @staticmethod
    def __tagFormat(tags):
        return tags.replace(' ','+')

    @staticmethod
    def __getFileType(url):
        lastQuestionMark = url.rfind('?')
        lastDotBeforeQM = url.rfind('.',0,lastQuestionMark)
        #remove everything before first?get
        return url[lastDotBeforeQM:lastQuestionMark]
    #endregion

    def get_posts(self, page = 0):
        if(page == 0):
            #page is not specified, so i get them all
            self.posts = []
            temp = [0]
            while(len(temp) != 0):
                page+=1
                temp = self.get_posts(page)
                self.posts.extend(temp)
        else:
            print("G("+self.tags+"):"+str(page))
            return Sankaku.__getUrlJsonToObject(Settings.API_URL + 'posts?lang=english&page='+str(page)+'&limit=100&tags='+Sankaku.__tagFormat(self.tags))
        return self.posts

    @staticmethod
    def download_post(post, folder):
        req = urllib.request.Request(
            post[Settings.POST_URL], 
            data=None, 
            headers= Settings.HTTP_HEADERS
        )
        filename = folder+"\\"+str(post[Settings.POST_ID]) + Sankaku.__getFileType(post[Settings.POST_URL])
        datatowrite = urllib.request.urlopen(req).read()
        with open(filename, 'wb') as f:
            f.write(datatowrite)
            f.close()
    #endregion

    def __init__(self,tags,folder,print = None):
        self.tags = tags
        self.folder = folder
        self.print = print

    def output(self, string):
        if(callable(self.print)): self.print(string)

    def download(self):
        self.progress = 0
        posts = self.get_posts()
        self.total = len(posts)
        for i in range(self.total):
            self.output("D("+str(i+1)+"/"+str(self.total)+"):"+ str(posts[i][Settings.POST_ID]))
            Sankaku.download_post(posts[i],self.folder)
            self.progress += 1;
        self.output("Complete")
