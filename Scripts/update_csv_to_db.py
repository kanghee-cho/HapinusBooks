# -*- coding: utf-8 -*-
# ========================================================================
# CSV 파일을 읽어서 DB에 업데이트하는 스크립트
# ------------------------------------------------------------------------
# Filename: update_csv_to_db.py
# Usage: python update_csv_to_db.py
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
import time

import psycopg2
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()
LOG_LEVEL = os.getenv("LOG_LEVEL", "ERROR").upper()
LOG_FILE_PATH = "../logs/update_csv_to_db.log"
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.ERROR),
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE_PATH, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
# DB 연결 설정
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
}

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


def get_or_create(cursor, table, column, value):
    """
    테이블에서 값이 존재하면 ID를 반환하고, 없으면 새로 생성 후 ID를 반환합니다.
    :param cursor: 데이터베이스 커서
    :param table: 테이블 이름
    :param column: 검색할 열 이름
    :param value: 검색할 값
    :return: 해당 값의 ID
    """
    cursor.execute(f"SELECT {table}_id FROM {table} WHERE {column} = %s", (value,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        cursor.execute(
            f"INSERT INTO {table} ({column}) VALUES (%s) RETURNING {table}_id", (value,)
        )
        return cursor.fetchone()[0]

def read_book_info_csv(filename):
    """
    CSV 파일에서 책 정보를 읽어 리스트로 반환합니다.
    :param filename: CSV 파일 경로
    :return: 책 정보 리스트
    """
    book_info_list = []
    if os.path.exists(filename):
        with open(filename, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                book_info_list.append(row)
    return book_info_list

def update_books_in_db(book_info_list):
    """
    CSV 파일에서 읽은 책 정보를 데이터베이스에 업데이트합니다.
    :param book_info_list: 책 정보 리스트
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        for book in book_info_list:
            isbn_key = book["ISBN_KEY"]
            is_updated = book["IS_UPDATED"].strip().upper() == "TRUE"

            if not is_updated:
                continue

            # 카테고리, 태그, 저자, 번역가, 출판사, 출판일 처리
            category_id = get_or_create(cursor, "category", "name", book["CATEGORY"])
            tag_ids = [
                get_or_create(cursor, "tag", "name", tag.strip())
                for tag in book["TAGS"].split(",") if tag.strip()
            ]
            author_ids = [
                get_or_create(cursor, "author", "name", author.strip())
                for author in book["AUTHORS"].split(",") if author.strip()
            ]
            translator_ids = [
                get_or_create(cursor, "translator", "name", translator.strip())
                for translator in book["TRANSLATORS"].split(",") if translator.strip()
            ]
            publisher_id = get_or_create(cursor, "publisher", "name", book["PUBLISHER"])

            # 책 정보 업데이트
            cursor.execute(
                """
                INSERT INTO book (isbn_key, title, subtitle, original_title,
                                  publisher_id, published_date, pages,
                                  edition, rating, review_text,
                                  description, thumbnail_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s,
                        %s, %s::numeric(3, 2), %s,
                        %s, %s)
                ON CONFLICT (isbn_key) DO UPDATE SET
                    title = EXCLUDED.title,
                    subtitle = EXCLUDED.subtitle,
                    original_title = EXCLUDED.original_title,
                    publisher_id = EXCLUDED.publisher_id,
                    published_date = EXCLUDED.published_date,
                    pages = EXCLUDED.pages,
                    edition = EXCLUDED.edition,
                    rating = EXCLUDED.rating,
                    review_text = EXCLUDED.review_text,
                    description = EXCLUDED.description,
                    thumbnail_url = EXCLUDED.thumbnail_url
                RETURNING book_id
                """,
                (
                    isbn_key,
                    book["TITLE"],
                    book["SUBTITLE"],
                    book["ORIGINAL_TITLE"],
                    publisher_id,
                    book["PUBLISHED_DATE"],
                    book["PAGES"],
                    book["EDITION"],
                    book["RATING"],
                    book["REVIEW_TEXT"],
                    book["DESCRIPTION"],
                    book["THUMBNAIL_URL"],
                ),
            )
            book_id = cursor.fetchone()[0]
            logging.info("Updated book with ISBN_KEY: %s", isbn_key)
            # 카테고리와 책 연결
            cursor.execute(
                "INSERT INTO book_category (book_id, category_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                (book_id, category_id),
            )
            # 태그와 책 연결
            for tag_id in tag_ids:
                cursor.execute(
                    "INSERT INTO book_tag (book_id, tag_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                    (book_id, tag_id),
                )
            # 저자와 책 연결
            for author_id in author_ids:
                cursor.execute(
                    "INSERT INTO book_author (book_id, author_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                    (book_id, author_id),
                )


if __name__ == "__main__":

