import urllib.request as url_req
from bs4 import BeautifulSoup
from config import config, update_recent_article
from slack_notification import slack_notify

first_view = url_req.urlopen(config['web_info']['url']).read()
soup = BeautifulSoup(first_view, "lxml")

def extract_pick_up(soup=soup):
    """
    指定されたページのhtmlを読み込み、pick upの記事を抜粋してくる
    """
    columns = soup.find_all("dl", class_="clearfix")
    return columns


def extract_url(column):
    """
    columns @params: コラムのurlを抽出する
    """
    column_html = BeautifulSoup(str(column), "lxml")
    url = column_html.find("a").get("href")
    return url


def extract_update_article(columns):
    """
    更新された記事を抽出
    更新前の最新の記事のindexはconfig.iniで管理
    """
    # 最新の記事番号を取得
    recent_article = config['web_info']['recent_article']
    # 更新された記事のurlを取得
    url_list = []
    update_start = False
    # 逆順に取得していき、最新記事の次からの記事のurlを取得
    for column in reversed(columns):
        url = extract_url(column)
        article_num = url.replace(config['web_info']['url']+"/", "")
        # 取得すべきurl
        if update_start:
            url_list.append(url)
            recent_article = article_num
            continue
        # 前回取得した最新の記事かどうか判定
        if recent_article == article_num:
            update_start = True

    # config更新
    update_recent_article(recent_article)
    if url_list == []:
        return ["更新記事はありません"]
    return url_list


if __name__ == "__main__":
    columns = extract_pick_up()
    url = extract_url(columns[0])
    url_list = extract_update_article(columns)
    slack_notify(text_="プロたんの記事", list_=url_list)
