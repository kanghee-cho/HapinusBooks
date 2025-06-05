# -*- coding: utf-8 -*-
# ========================================================================
# ISBN 정보를 읽어서 Kakao API를 통해 책 정보를 가져오고 CSV로 저장하는 스크립트
# ------------------------------------------------------------------------
# Filename: kakao_isbn_processor_to_csv.py
# Usage: python kakao_isbn_processor_to_csv.py
# ------------------------------------------------------------------------
# Author: KH.CHO
# Version: 1.0.1
# ------------------------------------------------------------------------
# History:
# v1.0.0 - Initial version (2024-06-04)
# V1.0.1 - Refactored File I/O handling (2024-06-04)
# ========================================================================

import csv
import json
import logging
import os
import sys
import time

import requests
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

LOG_LEVEL = os.getenv("LOG_LEVEL", "ERROR").upper()
LOG_FILE_PATH = "../logs/kakao_isbn_processor.log"
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.ERROR),
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE_PATH, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

KAKAO_BOOK_API_URL = "https://dapi.kakao.com/v3/search/book"
KAKAO_API_KEY = os.getenv("KAKAO_API_KEY")

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

if not KAKAO_API_KEY:
    raise ValueError(
        "KAKAO_API_KEY is not set. Please ensure the environment variable is defined in your .env file."
    )


def read_book_info_csv(filename):
    """
    CSV 파일에서 리스트를 읽고, IS_UPDATED가 False인 항목의 ISBN_KEY를 반환하는 함수
    :param filename: CSV 파일 경로
    """
    isbn_key_list = []
    if os.path.exists(filename):
        with open(filename, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            isbn_key_list = [
                row["ISBN_KEY"]
                for row in reader
                if row["IS_UPDATED"].strip().upper() == "FALSE"
            ]
    return isbn_key_list


def json_to_book_dictionary(isbn_key, book_json):
    """
    Kakao API에서 반환된 JSON 데이터를 책 정보 딕셔너리로 변환
    :param isbn_key: ISBN 키
    :param book_json: Kakao API에서 반환된 JSON 데이터
    """
    if not book_json or "documents" not in book_json or not book_json["documents"]:
        logging.warning("유효한 책 정보를 찾을 수 없습니다.")
        return None

    book = book_json["documents"][0]

    raw_isbn_str = book.get("isbn", "").strip()  # ISBN 문자열에서 공백 제거
    isbn10 = ""
    isbn13 = ""

    if raw_isbn_str:
        parts = raw_isbn_str.split()  # 공백으로 분리
        if len(parts) == 1:
            part1 = parts[0].strip()
            if len(part1) == 10 and part1.isdigit():
                isbn10 = part1
            elif len(part1) == 13 and part1.isdigit():
                isbn13 = part1
        elif len(parts) >= 2:
            part1 = parts[0].strip()
            part2 = parts[1].strip()
            if len(part1) == 10 and part1.isdigit():
                isbn10 = part1
            elif len(part1) == 13 and part1.isdigit():
                isbn13 = part1
            if len(part2) == 10 and part2.isdigit():
                isbn10 = part2
            elif len(part2) == 13 and part2.isdigit():
                isbn13 = part2

    book_details = {
        "ISBN_KEY": isbn_key,
        "IS_UPDATED": "TRUE",
        "TITLE": book.get("title", ""),
        "SUBTITLE": "",
        "ORIGINAL_TITLE": "",
        "AUTHORS": book.get("authors", []),
        "TRANSLATORS": book.get("translators", []),
        "PUBLISHER": book.get("publisher", ""),
        "PUBLISHED_DATE": book.get("datetime", "").split("T")[0],
        "ISBN_10": isbn10,
        "ISBN_13": isbn13,
        "PAGES": "",
        "EDITION": "",
        "CATEGORY": "",
        "TAGS": "",
        "RATING": "",
        "REVIEW_TEXT": "",
        "HEX1": "",
        "HEX2": "",
        "HEX3": "",
        "HEX4": "",
        "HEX5": "",
        "HEX6": "",
        "THUMBNAIL_URL": book.get("thumbnail", ""),
        "DESCRIPTION": book.get("contents", ""),
    }
    return book_details


def get_book_info_from_kakao_api(isbn_key):
    """
    ISBN 키를 사용하여 Kakao API에서 책 정보를 가져오고, JSON 데이터를 책 정보 딕셔너리로 변환
    :param isbn_key: ISBN 키
    :return: 책 정보 딕셔너리 또는 None
    """
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params = {"query": isbn_key, "target": "isbn"}

    try:
        response = requests.get(
            KAKAO_BOOK_API_URL, headers=headers, params=params, timeout=10
        )
        response.raise_for_status()  # HTTP 오류 발생 시 예외 발생

        data = response.json()  # 응답을 JSON 객체로 파싱
        logging.debug("--- ISBN [%s] API 응답 전체 (JSON) ---", isbn_key)
        # JSON 데이터를 예쁘게 포맷팅하여 출력 (들여쓰기 및 한글 인코딩 처리)
        logging.debug(json.dumps(data, indent=4, ensure_ascii=False))

        return data  # 파싱된 JSON 객체 전체 반환

    except requests.exceptions.Timeout:
        logging.error("ISBN %s 처리 중 타임아웃 발생.", isbn_key)
    except requests.exceptions.ConnectionError:
        logging.error("ISBN %s 처리 중 네트워크 연결 오류 발생.", isbn_key)
    except requests.exceptions.HTTPError as http_err:
        logging.error("ISBN %s 처리 중 HTTP 오류 발생: %s", isbn_key, http_err)
    except Exception as e:
        logging.error("ISBN %s 처리 중 알 수 없는 오류 발생: %s", isbn_key, e)

    return None


def write_csv_rows(filename, rows):
    """
    Helper function to write rows to a CSV file.
    :param filename: CSV 파일 경로
    :param rows: CSV에 저장할 데이터 리스트
    """
    with open(filename, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=BOOK_INFO_HEADER)
        writer.writeheader()
        writer.writerows(rows)


def save_book_info_to_csv(book_info, filename):
    """
    책 정보를 CSV 파일에 저장
    :param book_info: 책 정보 딕셔너리
    :param filename: CSV 파일 경로
    """
    if not book_info:
        logging.error("저장할 책 정보가 없습니다.")
        return

    rows = []
    if os.path.exists(filename):
        with open(filename, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            rows = list(reader)

    updated = False
    for i, row in enumerate(rows):
        if row["ISBN_KEY"] == book_info["ISBN_KEY"]:
            rows[i] = book_info
            updated = True
            logging.info("책 정보가 %s에서 업데이트되었습니다.", filename)
            break

    if not updated:
        rows.append(book_info)
        logging.info("책 정보가 %s에 추가되었습니다.", filename)

    write_csv_rows(filename, rows)


if __name__ == "__main__":
    logging.info("===============================")
    logging.info("DateTime: %s", time.strftime("%Y-%m-%d %H:%M:%S"))
    logging.info(
        "Starting the script to fetch book information using Kakao API and save it to a CSV file."
    )
    logging.info("--------------------------------")
    isbn_key_list = read_book_info_csv(BOOK_INFO_FILENAME)

    if not isbn_key_list:
        logging.info("No ISBN_KEYs to process. Exiting the program.")
        sys.exit(0)
    else:
        logging.info("List of ISBN_KEYs to process: %s", isbn_key_list)
        for isbn_key in isbn_key_list:
            logging.info("Processing ISBN_KEY: %s", isbn_key)
            book_info = get_book_info_from_kakao_api(isbn_key)
            if book_info:
                book_details = json_to_book_dictionary(isbn_key, book_info)
                if book_details:
                    save_book_info_to_csv(book_details, BOOK_INFO_FILENAME)
                    logging.info(
                        "Successfully processed and saved ISBN_KEY: %s", isbn_key
                    )
                else:
                    logging.warning(
                        "Failed to convert book information for ISBN_KEY: %s", isbn_key
                    )
            else:
                logging.error(
                    "Failed to fetch book information for ISBN_KEY: %s", isbn_key
                )
        logging.info("Finished processing all ISBN_KEYs.")
    logging.info("===============================")
