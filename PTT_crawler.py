import os
import bs4
import time
import threading
import pandas as pd
import config as cfg
import urllib.request as req


class MyThread(threading.Thread):
    def __init__(self, broad_URL, last_index, HTML_list):
        threading.Thread.__init__(self)
        self.broad_URL = broad_URL
        self.last_index = last_index
        self.HTML_list = HTML_list

    def run(self):
        index = self.broad_URL.find('.html')
        broad_URL = self.broad_URL[:index] + str(self.last_index) + self.broad_URL[index:]
        try:
            HTML = _get_page_HTML(broad_URL)
        finally:
            self.HTML_list.append(HTML)


def get_broad_URL(broad_name):
    # TODO: check if broad_name is valid
    return 'https://www.ptt.cc/bbs/' + broad_name + '/index.html'


def crawl(broad_URL, total_page_num, key_words):
    all_posts = __get_all_posts(broad_URL, total_page_num, key_words)
    return all_posts


def __get_all_posts(broad_URL, total_page_num, key_words):
    threads = list()
    HTML_list = list()

    HTML = _get_page_HTML(broad_URL)
    HTML_list.append(HTML)
    url = __get_next_page(HTML)[1]
    last_index = url.split('index')[1].split('.')[0]
    last_index = int(last_index)

    for page in range(int(total_page_num) - 1):
        t = MyThread(broad_URL, last_index, HTML_list)
        threads.append(t)
        last_index -= 1

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    all_pages_post = __parse_HTML_list(HTML_list)
    if key_words != '/no':
        all_pages_post = __filter(all_pages_post, key_words)
    return all_pages_post


def __filter(all_pages_post, key_words):
    after_filer = list()
    key_word_list = key_words.split(' ')
    for per_page_posts in all_pages_post:
        per_page_list = [post for post in per_page_posts if _search(post, key_word_list)]
        after_filer.append(per_page_list)
    return after_filer


def _search(post, key_word_list):
    count = 0
    put_in = False
    for key in key_word_list:
        if key.lower() in post['title'].lower():
            count += 1
    if count == len(key_word_list):
        put_in = True
    return put_in


def __parse_HTML_list(HTML_list):
    all_pages_post = list()
    for HTML in HTML_list:
        all_pages_post.append(__get_page_detail(HTML))
    return all_pages_post


def __get_page_detail(HTML):
    all_metadata = HTML.find_all('div', class_='r-ent')

    posts = list()

    for metadata in all_metadata:
        element = metadata.find('div', 'title').find('a')
        if element:
            posts.append({
                'push': metadata.find('div', 'nrec').get_text(),
                'title': element.get_text(),
                'link': element.get('href'),
                'author': metadata.find('div', 'author').get_text(),
                'date': metadata.find('div', 'date').get_text()
            })

    return posts


def _get_page_HTML(broad_url):
    request = __add_headers(broad_url)
    try:
        with req.urlopen(request) as response:
            HTML = response.read().decode('utf-8')
    except Exception as e:
        print('The URL \'{}\' is unValid! @Cause:{}', broad_url, e)
        return None
    HTML = bs4.BeautifulSoup(HTML, 'html.parser')
    return HTML


def __add_headers(url):
    request = req.Request(url, headers={
        'cookie': 'over18=1',
        'User-Agent': cfg.getRandomHeader()
    })
    return request


def __get_next_page(HTML):
    btn_group = HTML.find('div', class_='btn-group btn-group-paging')

    btn_list = [btn_wide.get('href') for btn_wide in btn_group.select('a') if btn_wide.get('href') is not None]

    return btn_list


def list_all_posts(all_posts):
    count = 0
    print(f'+===============================================================+')
    for i in range(len(all_posts)):
        for post in all_posts[i]:
            count += 1
            url = 'https://www.ptt.cc/' + post['link']
            count, title, url, date = count, post['title'], url, post['date']
            print(f'+{count:6d}| {title:45}')
            print(f'+{date:>6}| {url:45}')
            print(f'+===============================================================+')


def save_to_csv(all_posts):
    dfs = pd.DataFrame()
    for i in range(len(all_posts)):
        titles = [entry['title'] for entry in all_posts[i]]
        links = [entry['link'] for entry in all_posts[i]]
        dates = [entry['date'] for entry in all_posts[i]]
        authors = [entry['author'] for entry in all_posts[i]]
        pushes = [entry['push'] for entry in all_posts[i]]
        df = pd.DataFrame({
            'push': pushes,
            'title': titles,
            'link': links,
            'author': authors,
            'date': dates
        })
        dfs = pd.concat([dfs, df], axis=0)

    abspath = os.path.split(os.path.abspath('PTT_crawler.py'))[0]
    path = abspath + '\\PTT_Crawler_{}.csv'.format(__get_local_time())
    dfs.to_csv(path, index=False, columns=['push', 'title', 'link', 'author', 'date'], encoding='utf_8_sig')


def __get_local_time():
    localtime = time.localtime()
    return time.strftime("%Y%m%d_%H%M%S", localtime)