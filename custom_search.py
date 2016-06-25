# -*- coding: utf-8 -*-
import urllib.request as request
import urllib.parse as parse
from urllib.error import HTTPError
import json
import os
from bs4 import BeautifulSoup
import re
from PIL import Image
import time

from googleapiclient.discovery import build


# イメージを保存する
IMAGE_DIR = os.path.dirname(os.path.abspath(__file__)) + "/images"

# 取得したgoogle関連情報
GOOGLE_API_KEY = "*********"
GOOGLE_ENGINE_ID = "**********"


class CustomSearch(object):

    api_key = ""
    engine_id = ""

    def __init__(self, api_key, engine_id):
        """
        コンストラクタ
        googleの情報を格納する
        """
        self.api_key = api_key
        self.engine_id = engine_id

    def get_image_info(self, search_word, start=1):
        """
        Google CustomSearch で画像検索と画像情報を取得する
        """

        service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
        res = service.cse().list(q=search_word,
                                 cx=GOOGLE_ENGINE_ID,
                                 alt="json",
                                 lr="lang_ja",
                                 searchType="image").execute()

        image_info = []
        for item in res["items"]:

            extension = re.match("image/(.*)", item["mime"]).group(1)
            if extension == "":
                extension = "jpeg"

            image_info.append(
                {
                    'link': item["link"],
                    'extension': extension
                })

        return image_info

    def save_images(self, word, max_count=100, resize=False):
        """
        画像を取得する
        """

        dir_name = IMAGE_DIR + "/" + word + "/"

        if not os.path.exists(dir_name):
            os.mkdir(dir_name)

        for start in range(1, max_count+1):
            image_info = self.get_image_info(word, start)
            for image in image_info:
                file_name = self.create_file_name(
                    dir_name, image["link"], image["extension"])
                file_path = dir_name + file_name

                print(image["link"])

                try:
                    connection_test = request.urlopen(image["link"])
                except (HTTPError, OSError) as e:
                    continue

                request.urlretrieve(image["link"], file_path)

                if resize is True:
                    self.resize_image(file_path, image["extension"])


            # APIの接続制限があるため、5秒ごとにあける
            time.sleep(5)

    def count_dir_files(self, dir_path):
        """
        画像のファイル名をつけるために、画像を保存している
        ディレクトリから画像の個数をカウントする
        """
        count = 0
        for f in os.listdir(dir_path):
            count += 1

        return count

    def create_file_name(self, dir_name, link, ext):
        """
        保存する画像の名前を作る
        """

        file_count = self.count_dir_files(dir_name)

        return str(file_count).zfill(8) + "." + ext

    def resize_image(self, file_path, ext):
        """
        機会学習用に画像を圧縮する
        """

        img = Image.open(file_path, 'r')
        resize_img = img.resize((100, 100))
        resize_img.save(file_path, ext.upper(), quality=100, optimize=True)



if __name__ == '__main__':
    
    custom_search = CustomSearch(GOOGLE_API_KEY, GOOGLE_ENGINE_ID)
    custom_search.save_images("cat", max_count=1, resize=False)

