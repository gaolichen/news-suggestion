class NewsSiteBase(object):
    def is_news_page(self, url):
        raise NotImplemented

    def clean_title(self, title, url):
        raise NotImplemented

def rstrip(title, sep):
    pos = title.find(sep)
    if pos >= 0:
        return title[:pos]
    else:
        return title

class SinaNews(NewsSiteBase):
    def __init__(self):
        super(SinaNews, self).__init__()
        self.domain = 'sina.com.cn'
    
    def is_news_page(self, url):
        return self.domain in url and (url.endswith('html') or url.endswith('shtml')) and not 'slide' in url and not '/comment' in url
    
    def clean_title(self, title, url):
        title = rstrip(title, u'|')
        return rstrip(title, u'_')

class BackchinaNews(NewsSiteBase):
    def __init__(self):
        super(BackchinaNews, self).__init__()
        self.domain = 'backchina.com'
    
    def is_news_page(self, url):
        return f'{self.domain}/news/' in url and url.endswith('html')
    
    def clean_title(self, title, url):
        return rstrip(title, '-').strip()

class DWNews(NewsSiteBase):
    def __init__(self):
        super(DWNews, self).__init__()
        self.domain = 'dwnews.com'
    
    def is_news_page(self, url):
        if not self.domain in url:
            return False
        
        if 'blog.dwnews.com' in url and url.endswith('.html'):
            return True

        parts = url.split('/')
        if len(parts) < 5:
            return False
            
        return parts[-2].isdigit()
    
    @staticmethod
    def _title_from_url(url):
        pos = url.rfind('/')
        if pos >= 0:
            return url[pos + 1:]
        else:
            return ''
    
    def clean_title(self, title, url):
        title = rstrip(title, u'|')
        title = rstrip(title, u'_')

        if '/blog.' in url:
            return title
        
        title2 = self._title_from_url(url)
        if len(title2) > len(title):
            return title2
        else:
            return title

all_news_sites = [DWNews(), SinaNews(), BackchinaNews()]