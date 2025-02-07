from scholarly import scholarly
import requests
from bs4 import BeautifulSoup

import threading
import time
from scholarly import scholarly
from datetime import datetime

from ref_graph.prompts.prompts import (
    PAPER_COMPARE_PROMPT,
    REQUEST_HTML_PARSING_PROMPT,
    REQUEST_REAL_CITATION_PROMPT,
)


def get_citation_count_using_scholarly(
    ref_paper_title, ref_paper_authors, ref_paper_source, comp_try_limit=20, TIMEOUT=20
):  # 타임아웃 설정 추가

    print(f"\tSearch using scholarly")

    # ✅ 검색 수행을 위한 쓰레드 클래스
    class ScholarlyThread(threading.Thread):
        def __init__(self):
            super().__init__()
            self.result = None

        def run(self):
            try:
                self.result = scholarly.search_pubs(ref_paper_title)
            except Exception as e:
                self.result = None

    # ✅ 실행 시간 측정 및 타임아웃 적용
    def search_with_timeout():
        thread = ScholarlyThread()
        thread.start()
        thread.join(TIMEOUT)  # 타임아웃 적용

        if thread.is_alive():
            print(f"⏳ Timeout {TIMEOUT} sec exceeded! Moving to the next step.")
            return None  # 타임아웃 발생 시 None 반환
        return thread.result  # 성공하면 결과 반환

    # ✅ Google Scholar에서 논문 검색 (타임아웃 적용)
    search_query = search_with_timeout()

    if search_query is None:
        print(f"\tscholarly search timed out or failed")
        return None

    cnt = 0
    if not len(search_query._rows):  # 검색 결과 없을 때
        print(f"\tscholarly no result")
        return None

    for result in search_query:
        cnt += 1
        b_paper_title = result["bib"]["title"]
        b_paper_authors = ", ".join(result["bib"]["author"])
        b_paper_source = result.get("pub_url", "")

        # ✅ 논문 비교 (paper_compare 함수 사용)
        if (
            paper_compare(
                ref_paper_title,
                ref_paper_authors,
                ref_paper_source,
                b_paper_title,
                b_paper_authors,
                b_paper_source,
            )
            == "YES"
        ):
            citation_count = result.get("num_citations", 0)  # 인용수 가져오기
            return {
                "title": b_paper_title,
                "authors": b_paper_authors,
                "citation_count": {
                    "value": citation_count,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                },
            }

        # 검색 횟수 제한 도달 시 종료
        if cnt >= comp_try_limit:
            print(f"scholarly couldn't find a match within {comp_try_limit} attempts")
            return None


from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

from openai import OpenAI
client = OpenAI()

def get_citation_count_using_request(ref_paper_title, ref_paper_authors):
    print(f"\tSearch using Request")
    url = f"https://scholar.google.com/scholar?q={ref_paper_title}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)

    # 상태 코드 확인
    if (response.status_code == 200) and (response.text != ""):
        # HTML 파싱
        soup = BeautifulSoup(response.text, "html.parser")

        # 논문 제목과 관련 정보 추출
        results = soup.select(".gs_ri")
        print(f"\t# of results : {len(results)}")
        if not len(results):
            return None
        request_box_collect = ""
        for one_paper_box_html in results:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": REQUEST_HTML_PARSING_PROMPT.format(
                            one_paper_box_html=one_paper_box_html
                        ),
                    },
                ],
            )
            answer = response.choices[0].message.content
            request_box_collect += (
                answer.replace("```json", "").replace("```", "") + "\n"
            )

        print(f"\trequest_box_collect : \n\t{request_box_collect}")
        answer = llm.invoke(
            REQUEST_REAL_CITATION_PROMPT.format(
                ref_paper_title=ref_paper_title,
                ref_paper_authors=ref_paper_authors,
                request_box_collect=request_box_collect,
            )
        )
        if answer.content != "NO":
            answer_dict = eval(answer.content.replace("```json", "").replace("```", ""))
            answer_dict["citation_count"]["date"] = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            return answer_dict
        else:
            return None

    else:
        print(f"get_citation_count_using_scholarly : BAD Response")
        return None


def paper_compare(
    ref_paper_title,
    ref_paper_authors,
    ref_paper_source,
    b_paper_title,
    b_paper_authors,
    b_paper_source,
):
    print(
        f"\tΓref_paper_title : {ref_paper_title}({ref_paper_authors[:20]}...)\n\tL  b_paper_title : {b_paper_title}({b_paper_authors[:20]}...)"
    )
    prompt = PAPER_COMPARE_PROMPT.format(
        a_paper_title=ref_paper_title,
        a_paper_authors=ref_paper_authors,
        a_paper_source=ref_paper_source,
        b_paper_title=b_paper_title,  # 오타 수정
        b_paper_authors=b_paper_authors,
        b_paper_source=b_paper_source,
    )
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt},
        ],
    )
    answer = response.choices[0].message.content
    print(f"\t{answer}")
    return answer
