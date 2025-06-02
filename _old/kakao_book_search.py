import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()
KAKAO_API_KEY = os.getenv("KAKAO_API_KEY")

if not KAKAO_API_KEY:
    raise ValueError("KAKAO_API_KEY is not set in the environment variables.")


def get_book_info(isbn):
    """ISBN을 이용하여 카카오 책 검색 API를 호출하고, 응답을 JSON 객체로 파싱하여 반환"""
    api_url = "https://dapi.kakao.com/v3/search/book"
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params = {"query": isbn, "target": "isbn"}
    try:
        response = requests.get(api_url, headers=headers, paams=params, timeout=10)
        response.raise_for_status()

        data = response.json()  # 응답을 JSON 객체로 파싱

        print(f"\n--- ISBN [{isbn}] API 응답 전체 (JSON) ---")
        # JSON 데이터를 예쁘게 포맷팅하여 출력 (들여쓰기 및 한글 인코딩 처리)
        print(json.dumps(data, indent=4, ensure_ascii=False))

        return data  # 파싱된 JSON 객체 전체 반환

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP 에러 발생: {http_err}")
        print(f"응답 코드: {response.status_code}, 응답 내용: {response.text}")
        return None
    except requests.exceptions.RequestException as req_err:
        print(f"요청 중 에러 발생: {req_err}")
        return None
    except json.JSONDecodeError:  # 혹시 모를 파싱 에러에 대비
        print("JSON 응답을 파싱하는 데 실패했습니다.")
        return None
    except Exception as e:
        print(f"알 수 없는 에러 발생: {e}")
        return None


def extract_book_details(book_json):
    """책 검색 API의 개별 도서 응답(Document) JSON 객체에서 주요 정보를 추출하여 Dictionary로 반환"""
    if not book_json:
        return None

    title = book_json.get("title", "")
    authors = book_json.get("authors", [])
    translators = book_json.get("translators", [])
    publisher = book_json.get("publisher", "")
    datetime = book_json.get("datetime", "")  # 출판일
    published_date = datetime.split("T")[0] if datetime else ""
    raw_isbn_str = book_json.get("isbn", "").strip()  # ISBN 문자열에서 공백 제거
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

    book_info = book_json.get("contents", "")
    thumbnail = book_json.get("thumbnail", "")

    return {
        "title": title,
        "authors": authors,
        "translators": translators,
        "publisher": publisher,
        "published_date": published_date,
        "isbn10": isbn10,
        "isbn13": isbn13,
        "book_info": book_info,
        "thumbnail": thumbnail,
    }


if __name__ == "__main__":
    isbn = input("검색할 ISBN을 입력하세요: ").strip()
    if isbn:
        get_book_info(isbn)
    else:
        print("ISBN을 입력하지 않았습니다.")
