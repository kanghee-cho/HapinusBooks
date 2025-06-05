# -*- coding: utf-8 -*-
# ========================================================================
# CSV 파일에서 THUMBNAIL_URL읽어서 이미지를 다운로드 받아, 별도로 저장하는 스크립트
# ------------------------------------------------------------------------
# Filename: download_image.py
# Usage: python download_image.py
# ------------------------------------------------------------------------
# Author: KH.CHO
# Version: 1.0.0
# ------------------------------------------------------------------------
# History:
# v1.0.0 - Initial version (2024-06-05)
# ========================================================================
import csv
import logging
import os
import sys

import requests
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()
LOG_LEVEL = os.getenv("LOG_LEVEL", "ERROR").upper()
LOG_FILE_PATH = "../logs/download_image.log"
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.ERROR),
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE_PATH, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

# CSV 파일 이름 및 구조
BOOK_INFO_FILENAME = "../data/book_info.csv"
BOOK_INFO_HEADER = [
    "ISBN_KEY",
    "IS_UPDATED",
    "TITLE",
    "SUBTITLE",
    "ORIGINAL_TITLE",
    "AUTHORS",
    "TRANSLATORS",
    "PUBLISHER",
    "PUBLISHED_DATE",
    "ISBN_10",
    "ISBN_13",
    "PAGES",
    "EDITION",
    "CATEGORY",
    "TAGS",
    "RATING",
    "REVIEW_TEXT",
    "HEX1",
    "HEX2",
    "HEX3",
    "HEX4",
    "HEX5",
    "HEX6",
    "THUMBNAIL_URL",
    "DESCRIPTION",
]
# 이미지 저장 디렉토리
IMAGE_SAVE_DIR = "../data/images"
# 이미지 저장 디렉토리 생성
if not os.path.exists(IMAGE_SAVE_DIR):
    os.makedirs(IMAGE_SAVE_DIR)


# CSV 파일에서 책 정보 읽기
def read_book_info(filename):
    """주어진 CSV 파일에서 책 정보를 읽어 리스트로 반환합니다.
    :param filename: CSV 파일 경로
    :return: 책 정보 리스트
    """
    try:
        with open(filename, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file, fieldnames=BOOK_INFO_HEADER)
            next(reader)
            book_info_list = [row for row in reader]
        logging.info("Read %d book records from %s.", len(book_info_list), filename)
        return book_info_list
    except FileNotFoundError:
        logging.error("File %s not found.", filename)
        return []


def download_image(thumbnail_url, isbn_key):
    """
    주어진 썸네일 URL에서 이미지를 다운로드하고, ISBN_KEY를 파일 이름으로 저장합니다.
    :param thumbnail_url: 이미지 URL
    :param isbn_key: ISBN 키
    """

    try:
        # 이미지 파일이 있으면 다운로드하지 않음
        file_path = os.path.join(IMAGE_SAVE_DIR, f"{isbn_key}.jpg")
        if os.path.exists(file_path):
            logging.info(
                "Image for ISBN %s already exists at %s. Skipping download.",
                isbn_key,
                file_path,
            )
            return None

        response = requests.get(thumbnail_url, timeout=10)
        response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
        file_path = os.path.join(IMAGE_SAVE_DIR, f"{isbn_key}.jpg")
        with open(file_path, "wb") as file:
            file.write(response.content)
        logging.info("Downloaded image for ISBN %s to %s.", isbn_key, file_path)
    except requests.RequestException as e:
        logging.error("Failed to download image for ISBN %s: %s", isbn_key, e)
        return None
    except OSError as e:
        logging.error("File operation error for ISBN %s: %s", isbn_key, e)
        return None


def main():
    """
    메인 함수: CSV 파일에서 책 정보를 읽고, 썸네일 URL에서 이미지를 다운로드합니다.
    """
    book_info_list = read_book_info(BOOK_INFO_FILENAME)
    if not book_info_list:
        logging.warning("No book information found in %s.", BOOK_INFO_FILENAME)
        return

    for book in book_info_list:
        isbn_key = book.get("ISBN_KEY")
        thumbnail_url = book.get("THUMBNAIL_URL")
        logging.debug(
            "Processing book: ISBN_KEY=%s, THUMBNAIL_URL=%s",
            isbn_key,
            thumbnail_url,
        )
        if isbn_key and thumbnail_url:
            download_image(thumbnail_url, isbn_key)
        else:
            logging.warning("Missing ISBN_KEY or THUMBNAIL_URL for book: %s", book)
    logging.info("Image download process completed.")


if __name__ == "__main__":
    main()
    logging.info("Script finished successfully.")
    sys.exit(0)
