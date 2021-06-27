# ライブラリのインポート
import os
import webbrowser
from datetime import datetime
from urllib.request import urljoin, urlopen

from bs4 import BeautifulSoup as bs

# ログファイルの保存用ディレクトリパス
LOGDIR = "log"


# 利用する関数
def get_soup(target_url):
    """HTMLソースをBeautifulSoupで取得

    Args:
        target_url (string): 対象となるページのURL

    Returns:
        bs4.BeautifulSoup: BeautifulSoupでの結果の取得
    """
    return bs(urlopen(target_url).read().decode("utf8"), "html.parser")


def init_app():
    """ログディレクトリの作成
    """
    # ディレクトリが存在していたら何もしない
    if not os.path.exists(LOGDIR):
        os.mkdir(LOGDIR)
        print(f"ログ保存ディレクトリ「{LOGDIR}」を作成しました")


def load_log(site_name):
    """特定のサイトのログテキストから最新情報を取得

    Args:
        site_name (str): 対象とするサイトの名前

    Returns:
        str or None: 最新のログを返す（ログがない場合はNoneを返す）
    """
    log_path = os.path.join(
        LOGDIR, "[{}]check_log.txt".format(site_name))  # ログファイル
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


def write_log(site_name, log_data):
    """ログファイルに書き込む

    Args:
        site_name (string): 対象となるサイト
        log_data (string):  保存する内容
    """
    log_path = os.path.join(
        LOGDIR, "[{}]check_log.txt".format(site_name))  # ログファイル
    # ファイルの一番下に書き込み
    with open(log_path, "a", encoding="utf8") as fa:
        add_line = "{}\t{}\n".format(datetime.now(), log_data)
        fa.write(add_line)


# ↓サイトごとにこういった形でデータを取得する関数を作成する
def get_phc_latest_news():
    """pscのニュースページから最新の記事の情報を取得

    Returns:
        tupple: 最新記事をタプル（日付・タグ, タイトル, URL）で返す
    """
    # ソースの取得
    # 対象とするphcdのURL
    phc_base_url = "https://www.phchd.com/jp/"
    phc_news_lst_url = "https://www.phchd.com/jp/news"
    soup = get_soup(phc_news_lst_url)

    # ニューステーブルの情報を取得
    news_table_elms = soup.select("div.news_list dl")
    news_lst = []
    for news_table in news_table_elms:
        date_tag = news_table.select_one(
            "div dt").text.replace("\n", "").replace("\t", "")
        title = news_table.select_one("div dd").text.replace(
            "\n", "").replace("\t", "").replace(" ", "")
        url = urljoin(phc_base_url, news_table.select_one("dd a").get("href"))
        news_data = (date_tag, title, url)
        news_lst.append(news_data)
    # 最新のニュース記事のデータを取得
    latest_news_data = sorted(news_lst)[0]
    return latest_news_data


# メインの処理
if __name__ == "__main__":
    # 初期化
    init_app()

    # ログ中の最新更新日時の取得
    latest_date_tag = load_log("phc")
    if latest_date_tag:
        print("【前回取得時の最新記事】{}".format(latest_date_tag))

    # pscの最新の記事情報の取得
    latest_phc_news = get_phc_latest_news()

    if latest_date_tag == latest_phc_news[0]:
        # 前回取得時と同じ場合は何もしない
        print("\t更新なし")
    else:
        # 更新があった場合は
        print("\t更新あり\n{}".format(latest_phc_news[-1]))
        # ブラウザ立ち上げ
        webbrowser.open(latest_phc_news[-1])
        write_log("phc", "\t".join(latest_phc_news))
