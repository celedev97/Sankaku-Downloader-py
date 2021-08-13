from os import stat
import requests
import mimetypes
import json

# region Sankaku stuff
API_URL = "https://capi-v2.sankakucomplex.com/"
HTTP_HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'}

POST_ID = "id"
POST_URL = "file_url"
POST_MIME = "file_type"
# endregion

class Sankaku:
    __session: object = requests.Session()

    progress: int = 0
    total: int = 0
    statusMessage: str = "idle"

    posts: list = []


    def __init__(self, tags, folder, custom_url, print_fn = None):
        self.tags = tags
        self.folder = folder
        self.custom_url = custom_url
        self.print = print_fn

    @staticmethod
    def __getFileType(url: str): 
        lastQuestionMark = url.rfind('?')
        lastDotBeforeQM = url.rfind('.',0,lastQuestionMark)
        #remove everything before .:?
        return url[lastDotBeforeQM:lastQuestionMark]

    @staticmethod
    def download_post(post: dict, folder: str):
        if(post[POST_URL] == None):
            print(f"Can't download: {post}")

        r = Sankaku.__session.get(post[POST_URL])
        open(folder+"\\"+str(post[POST_ID]) + Sankaku.__getFileType(post[POST_URL]), 'wb').write(r.content)

    @staticmethod
    def get_info_from_id(id: int):
        # either returns a list of images or just one
        # Check the doujin api first before the normal one image post
        #### Doujin api
        res = Sankaku.__session.get(f'https://capi-v2.sankakucomplex.com/pools/{id}?lang=en')

        if res.status_code != 200:
            print(f'{id} is not a doujin/book, trying normal image api.')
        else:
            print(f'{id} is a doujin/book, reading data!')

            return res.json()['posts']

        #### Normal api
        res = Sankaku.__session.get(f'https://capi-v2.sankakucomplex.com/posts?lang=en&page=1&limit=1&tags=id_range:{id}')
        
        if res.status_code != 200:
            return print('Failed to get api data even on normal api, prolly an invalid id... Returning!')

        res = res.json()

        if len(res) == 0:
            return print('API returns nothing, returning...')

        return [res[0]]

    def get_posts(self):
        page = ""
        self.posts = []
        temp = [0]

        while(page != None):
            temp = self._getPage(page)
            page = temp['meta']['next']
            self.posts.extend(temp['data'])

        return self.posts

    def _getPage(self, page: int = None):
        print("G("+self.tags+"):"+ str(page))

        params = {
            'lang':'en',
            'limit':40,
            'tags':self.tags
        }

        if (page != None):
            params['next'] = page

        return json.loads(Sankaku.__session.get(API_URL + 'posts/keyset', params = params).content)

    def output(self, string: str):
        if(callable(self.print)): self.print(string)

    def download(self):
        Sankaku.__session.headers['User-Agent'] = HTTP_HEADERS['User-Agent']

        # Check if theres custom url or some shit
        if len(self.custom_url) > 0:
            self.output('Custom ID given, using that instead.')
            posts = Sankaku.get_info_from_id(self.custom_url)
        else:
            self.output('No custom url given, downloading based off tags.')
            self.progress = 0
            posts = self.get_posts()

        self.total = len(posts)
        for i in range(self.total):
            self.output("D("+ str(i+1) +"/" +str(self.total) +"):" + str(posts[i][POST_ID]))
            Sankaku.download_post(posts[i],self.folder)
            self.progress += 1

        self.output("Complete")
