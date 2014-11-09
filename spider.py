# -*- coding: utf-8 -*-

import urllib2
import urllib
import re
import os
import errno
import urlparse


class Spider:

    def __init__(self):
        self.index_filename = 'index.html'
        self.base_url = 'http://webapplayers.com/inspinia_admin-v1.5/'
        self.save_path = 'downloads/'

    def traversal_links(self, url):
        response = urllib2.urlopen(url)
        content = response.read().decode("utf-8")
        links = []

        # css
        p = re.compile(r'<link.+?href=.+?>')
        pname = re.compile( r'(?<=>)')
        phref = re.compile( r'(?<=href\=\").*?(?=\")')

        # TODO:javascript
        # TODO:images
        # TODO:fonts

        items = p.findall(content)
        for item in items:
            sname = pname.findall(item)
            if sname:
                sname = sname[0]
                shref = phref.findall(item)
            if shref:
                shref = shref[0]

            links.append(shref)
        return links

    def getdirc(self, url):
        idx = url.rfind('/')
        return url[:idx]

    # 下载到本地
    def download(self, url, save_path):
        # TODO:是否基路径就是首页

        # 除去文件名后的相对路径
        #if url != self.base_url:
        #    dir = self.getdirc(url)

        # 是否是下载的首页
        is_index_page = True

        if len(save_path) == 0:
            save_path = self.save_path

        if is_index_page:
            if not os.path.exists(self.save_path):
                self.mkdir_p(self.save_path)

            # 下载主页
            if not os.path.isfile(self.save_path + self.index_filename):
                urllib.urlretrieve(url, self.save_path + self.index_filename)
                print 'index page save as:' + self.index_filename

            # 下载其它资源文件
            links = self.traversal_links(url)
            for link in links:
                absolute_url = urlparse.urljoin(self.base_url, link)
                dirs = self.getdirc(save_path + link)
                if not os.path.exists(dirs):
                    self.mkdir_p(dirs)
                    print 'create directory:' + dirs

                    urllib.urlretrieve(absolute_url, save_path + link)
                    print 'download file:' + absolute_url

    # 递归创建文件夹
    def mkdir_p(self, path):
        try:
            os.makedirs(path)
        except OSError as exc: # Python >2.5 (except OSError, exc: for Python <2.5)
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise

if __name__ == "__main__":
    myModel = Spider()
    #url = raw_input('type url, please : ')
    #filename = raw_input('type main file name : ')
    myModel.download('http://webapplayers.com/inspinia_admin-v1.5/','')

