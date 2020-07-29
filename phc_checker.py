# ライブラリのインポート
import os
import webbrowser
from datetime import datetime
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen, urlretrieve, urljoin


# 利用する関数
def get_soup(target_url):
    """ソースをBeautifulSoupで取得

    Args:
        target_url (string): 対象となるページのURL

    Returns:
        bs4.BeautifulSoup: BeautifulSoupでの結果の取得
    """
    return bs(urlopen(target_url).read().decode("utf8"), "html.parser")


def load_log(site_name):
    log_path = os.path.join(
        "log", "[{}]check_log.txt".format(site_name))  # ログファイル
    if os.path.exists(log_path):
        # ファイルが存在したときは最新のログを読み込む
        with open(log_path, "r", encoding="utf8") as fobj:
            for line in fobj:
                date_tag = line.rstrip("\n").split("\t")[1]
                if date_tag == "更新なし":
                    break
                latest_date_tag = date_tag
            return latest_date_tag
    else:
        # ファイルがないときはログファイルの作成
        with open(log_path, "x", encoding="utf8") as fw:
            output_line = "{}\t処理スタート\n".format(datetime.now())
            fw.write(output_line)
        return "ログなし"


def add_log(site_name, log_data):
    """ログファイルに書き込む

    Args:
        site_name (string): 対象となるサイト
        log_data (string):  保存する内容
    """
    log_path = os.path.join(
        "log", "[{}]check_log.txt".format(site_name))  # ログファイル
    # ファイルの一番下に書き込み
    with open(log_path, "a", encoding="utf8") as fa:
        add_line = "{}\t{}\n".format(datetime.now(), log_data)
        fa.write(add_line)


def get_phc_latest_news():
    """pscのニュースページから最新の記事の情報を取得

    Returns:
        tupple: （日付・タグ, タイトル, URL）で返す
    """
    # ソースの取得
    phc_news_lst_url = "https://www.phchd.com/jp/news"
    soup = get_soup(phc_news_lst_url)

    # ニューステーブルの情報を取得
    news_table_elms = soup.select("div.news_list dl")

    news_lst = []
    for news_table in news_table_elms:
        date_tag = news_table.select_one("div dt").text  # 日付とタグ
        title = news_table.select_one("div dd").text  # タイトル
        url = urljoin(base_url[0], news_table.select_one(
            "dd a").get("href"))  # URL
        news_data = (date_tag, title, url)
        news_lst.append(news_data)

    # 最新のニュース記事のデータを取得
    latest_news_data = sorted(news_lst)[0]

    return latest_news_data


# メインの処理
if __name__ == "__main__":
    
    # 対象とするphcdのURL
    base_url = ("https://www.phchd.com/jp/",)
    
    # ログの読み込み
    latest_date_tag = load_log("phc")
    print("【最新投稿日】{}".format(latest_date_tag))

    # 最新の記事情報の取得
    latest_news_data = get_phc_latest_news()

    if latest_date_tag == latest_news_data[0]:
        # 最新のものと同じ
        print("更新なし")
        add_log("phc", "更新なし")
    else:
        print("更新あり\n{}".format(latest_news_data[-1]))
        # ブラウザ立ち上げ
        webbrowser.open(latest_news_data[-1])
        add_log("phc", "\t".join(latest_news_data))
