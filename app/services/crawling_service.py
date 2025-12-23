import requests
from bs4 import BeautifulSoup
import urllib3
import re
import time

# SSL 경고 무시
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_detail_info(pbancSn):
    """
    상세 페이지에서 요청된 항목들을 크롤링합니다.
    """
    url = f"https://www.k-startup.go.kr/web/contents/bizpbanc-ongoing.do?pbancClssCd=PBC010&schM=view&pbancSn={pbancSn}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # 기본값 설정
    info = {
        "tracks": [],
        "region": "",
        "target": "",
        "age": "",
        "period": "",
        "experience": "",
        "organizer": "",
        "required_docs": "",
        "deadline": ""
    }

    try:
        response = requests.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 1) 상단 요약 박스 파싱
        items = soup.select(".information_box-wrap ul li")
        for item in items:
            key_tag = item.select_one(".tit")
            val_tag = item.select_one(".txt")
            if key_tag and val_tag:
                key = key_tag.get_text(strip=True)
                val = val_tag.get_text(strip=True)

                if "지원분야" in key:
                    info["tracks"] = [x.strip() for x in val.split(",")]  # 리스트로 변환
                elif "지역" in key:
                    info["region"] = val
                elif "대상" in key and "연령" not in key:
                    info["target"] = val
                elif "대상연령" in key:
                    info["age"] = val
                elif "접수기간" in key:
                    info["period"] = val
                    # 마감일 추출 로직 (기간 문자열에서 뒤쪽 날짜 파싱)
                    dates = re.findall(r"\d{4}-\d{2}-\d{2}", val)
                    if len(dates) >= 2:
                        info["deadline"] = dates[1]
                    elif len(dates) == 1:
                        info["deadline"] = dates[0]
                elif "창업업력" in key:
                    info["experience"] = val
                elif "주관기관" in key:
                    info["organizer"] = val

        # 2) 제출서류 파싱
        info_lists = soup.select(".information_list")
        for section in info_lists:
            title_p = section.select_one(".title")
            if title_p and "제출서류" in title_p.get_text():
                doc_text = section.get_text(strip=True).replace("제출서류", "").strip()
                info["required_docs"] = doc_text

        return info

    except Exception as e:
        print(f"❌ 상세 페이지 파싱 실패 ({pbancSn}): {e}")
        return info


def crawl_k_startup(page_limit=1):
    """
    리스트를 순회하며 각 공고의 모든 정보를 수집합니다.
    """
    base_url = "https://www.k-startup.go.kr/web/contents/bizpbanc-ongoing.do"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    results = []

    for page in range(1, page_limit + 1):
        print(f"📡 {page}페이지 크롤링 중...")
        params = {"schM": "list", "pageIndex": page, "schStr": ""}

        try:
            response = requests.get(base_url, headers=headers, params=params, verify=False)
            soup = BeautifulSoup(response.text, 'html.parser')
            list_items = soup.select("#bizPbancList > ul > li")

            if not list_items:
                break

            for item in list_items:
                title_tag = item.select_one(".tit_wrap .tit")
                if not title_tag: continue

                title = title_tag.get_text(strip=True)

                # 공고 ID 및 URL 추출
                link_tag = item.select_one("a")
                pbanc_sn = None
                full_url = ""

                if link_tag:
                    href = link_tag.get('href')
                    match = re.search(r"go_view\((\d+)\)", href)
                    if match:
                        pbanc_sn = match.group(1)
                        full_url = f"https://www.k-startup.go.kr/web/contents/bizpbanc-ongoing.do?pbancClssCd=PBC010&schM=view&pbancSn={pbanc_sn}"

                if pbanc_sn:
                    # 상세 정보 가져오기
                    detail = get_detail_info(pbanc_sn)

                    # 수집된 데이터 통합
                    comp_data = {
                        "external_id": pbanc_sn,
                        "name": title,
                        "url": full_url,
                        # 상세 데이터 병합
                        "deadline": detail["deadline"],
                        "tracks": detail["tracks"],
                        "region": detail["region"],
                        "target": detail["target"],
                        "age": detail["age"],
                        "period": detail["period"],
                        "experience": detail["experience"],
                        "organizer": detail["organizer"],
                        "required_docs": detail["required_docs"],
                    }
                    results.append(comp_data)
                    time.sleep(0.5)  # 서버 부하 방지

        except Exception as e:
            print(f"❌ 크롤링 에러: {e}")

    return results