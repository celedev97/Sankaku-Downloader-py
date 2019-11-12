import requests
import mimetypes
import json
import Settings

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
        r = Sankaku.__session.get(post[Settings.POST_URL])
        open(folder+"\\"+str(post[Settings.POST_ID]) + Sankaku.__getFileType(post[Settings.POST_URL]), 'wb').write(r.content)
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
            params = {
                'lang':'english',
                'page':page,
                'limit':100,
                'tags':self.tags
            }
            return json.loads(Sankaku.__session.get(Settings.API_URL + 'posts',params = params).content)
        return self.posts

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
            self.progress += 1
        self.output("Complete")
