import json
import time
from django.conf import settings
from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import render

from neo4j_client import neo4j_client
from ref_graph.citation.get_citation import (
    get_citation_count_using_request,
    get_citation_count_using_scholarly,
)
from ref_graph.kdb_rag.rag_parser import RAG, RagParser
from ref_graph.models import UploadedFile
from ref_graph.form import FileUploadForm

from django.shortcuts import render, redirect

from django.http import JsonResponse
from llama_index.readers.file import PDFReader  # PDF 파일을 읽기 위한 리더
from openai import OpenAI
from django.views.decorators.csrf import csrf_exempt

client = OpenAI()
rag_parser = RagParser()

papers = {
    1: {
        "Title": "Language models are few-shot learners",
        "Author(s)": "Tom Brown, Benjamin Mann, Nick Ryder, Melanie Subbiah, Jared D Kaplan, Prafulla Dhariwal, Arvind Neelakantan, Pranav Shyam, Girish Sastry, Amanda Askell, et al.",
        "Conference": "Advances in neural information processing systems 33 (2020), 1877–1901",
        "citation_count": {"value": 39209, "date": "2025-01-28 21:45:37"},
    },
    2: {
        "Title": "Trends in distributed artificial intelligence",
        "Author(s)": "Brahim Chaib-Draa, Bernard Moulin, René Mandiau, and Patrick Millot",
        "Conference": "Artificial Intelligence Review 6 (1992), 35–66",
        "citation_count": {"value": 282, "date": "2025-01-28 21:45:46"},
    },
    3: {
        "Title": "Agentverse: Facilitating multi-agent collaboration and exploring emergent behaviors in agents",
        "Author(s)": "Weize Chen, Yusheng Su, Jingwei Zuo, Cheng Yang, Chenfei Yuan, Chen Qian, Chi-Min Chan, Yujia Qin, Yaxi Lu, Ruobing Xie, et al.",
        "Conference": "arXiv preprint arXiv:2308.10848 (2023)",
        "citation_count": {"value": 156, "date": "2025-01-28 21:45:49"},
    },
    4: {
        "Title": "Improving Factuality and Reasoning in Language Models through Multiagent Debate",
        "Author(s)": "Yilun Du, Shuang Li, Antonio Torralba, Joshua B Tenenbaum, and Igor Mordatch",
        "Conference": "arXiv preprint arXiv:2305.14325 (2023)",
        "citation_count": {"value": 446, "date": "2025-01-28 21:45:51"},
    },
    5: {
        "Title": "Recommender ai agent: Integrating large language models for interactive recommendations",
        "Author(s)": "Xu Huang, Jianxun Lian, Yuxuan Lei, Jing Yao, Defu Lian, and Xing Xie",
        "Conference": "arXiv preprint arXiv:2308.16505 (2023)",
        "citation_count": {"value": 79, "date": "2025-01-28 21:45:56"},
    },
    6: {
        "Title": "Camel: Communicative agents for 'mind' exploration of large scale language model society",
        "Author(s)": "Guohao Li, Hasan Abed Al Kader Hammoud, Hani Itani, Dmitrii Khizbullin, and Bernard Ghanem",
        "Conference": "arXiv preprint arXiv:2303.17760 (2023)",
        "citation_count": {"value": 531, "date": "2025-01-28 21:45:58"},
    },
    7: {
        "Title": "Webgpt: Browser-assisted question-answering with human feedback",
        "Author(s)": "Reiichiro Nakano, Jacob Hilton, Suchir Balaji, Jeff Wu, Long Ouyang, Christina Kim, Christopher Hesse, Shantanu Jain, Vineet Kosaraju, William Saunders, et al.",
        "Conference": "arXiv preprint arXiv:2112.09332 (2021)",
        "citation_count": {"value": 1108, "date": "2025-01-28 21:46:01"},
    },
    8: {
        "Title": "GPT-in-the-Loop: Adaptive Decision-Making for Multiagent Systems",
        "Author(s)": "Nathalia Nascimento, Paulo Alencar, and Donald Cowan",
        "Conference": "arXiv preprint arXiv:2308.10435 (2023)",
        "citation_count": {"value": 11, "date": "2025-01-28 21:46:07"},
    },
    9: {
        "Title": "GPT-4 Technical Report",
        "Author(s)": "OpenAI",
        "Conference": "arXiv preprint arXiv:2303.08774 (2023)",
        "citation_count": {"value": 7486, "date": "2025-01-28 21:46:10"},
    },
    10: {
        "Title": "Hugginggpt: Solving ai tasks with chatgpt and its friends in huggingface",
        "Author(s)": "Yongliang Shen, Kaitao Song, Xu Tan, Dongsheng Li, Weiming Lu, and Yueting Zhuang",
        "Conference": "arXiv preprint arXiv:2303.17580 (2023)",
        "citation_count": {"value": 1029, "date": "2025-01-28 21:46:13"},
    },
    11: {
        "Title": "RAH! RecSys-Assistant-Human: A Human-Central Recommendation Framework with Large Language Models",
        "Author(s)": "Yubo Shu, Hansu Gu, Peng Zhang, Haonan Zhang, Tun Lu, Dongsheng Li, and Ning Gu",
        "Conference": "arXiv preprint arXiv:2308.09904 (2023)",
        "citation_count": {"value": 17, "date": "2025-01-28 21:46:18"},
    },
    12: {
        "Title": "Multiagent systems: A survey from a machine learning perspective",
        "Author(s)": "Peter Stone and Manuela Veloso",
        "Conference": "Autonomous Robots 8 (2000), 345–383",
        "citation_count": {"value": 2064, "date": "2025-01-28 21:46:23"},
    },
    13: {
        "Title": "Collaborative-Enhanced Prediction of Spending on Newly Downloaded Mobile Games under Consumption Uncertainty",
        "Author(s)": "Peijie Sun, Yifan Wang, Min Zhang, Chuhan Wu, Yan Fang, Hong Zhu, Yuan Fang, and Meng Wang",
        "Conference": "WWW2024, Industry Track (2024)",
        "citation_count": {"value": 9, "date": "2025-01-28 21:46:29"},
    },
    14: {
        "Title": "Neighborhood-Enhanced Supervised Contrastive Learning for Collaborative Filtering",
        "Author(s)": "Peijie Sun, Le Wu, Kun Zhang, Xiangzhi Chen, and Meng Wang",
        "Conference": "IEEE Transactions on Knowledge and Data Engineering (2023)",
        "citation_count": {"value": 24, "date": "2025-01-28 21:46:34"},
    },
    15: {
        "Title": "Llama: Open and efficient foundation language models",
        "Author(s)": "Hugo Touvron, Thibaut Lavril, Gautier Izacard, Xavier Martinet, Marie-Anne Lachaux, Timothée Lacroix, Baptiste Rozière, Naman Goyal, Eric Hambro, Faisal Azhar, et al.",
        "Conference": "arXiv preprint arXiv:2302.13971 (2023)",
        "citation_count": {"value": 12263, "date": "2025-01-28 21:46:36"},
    },
    16: {
        "Title": "Grandmaster level in StarCraft II using multi-agent reinforcement learning",
        "Author(s)": "Oriol Vinyals, Igor Babuschkin, Wojciech M Czarnecki, Michaël Mathieu, Andrew Dudzik, Junyoung Chung, David H Choi, Richard Powell, Timo Ewalds, Petko Georgiev, et al.",
        "Conference": "Nature 575, 7782 (2019), 350–354",
        "citation_count": {"value": 5054, "date": "2025-01-28 21:46:42"},
    },
    17: {
        "Title": "When Large Language Model based Agent Meets User Behavior Analysis: A Novel User Simulation Paradigm",
        "Author(s)": "Lei Wang, Jingsen Zhang, Hao Yang, Zhiyuan Chen, Jiakai Tang, Zeyu Zhang, Xu Chen, Yankai Lin, Ruihua Song, Wayne Xin Zhao, et al.",
        "Conference": "arXiv preprint ArXiv:2306.02552 (2023)",
        "citation_count": {"value": 22, "date": "2025-01-28 21:46:45"},
    },
    18: {
        "Title": "Rec-mind: Large language model powered agent for recommendation",
        "Author(s)": "Yancheng Wang, Ziyan Jiang, Zheng Chen, Fan Yang, Yingxue Zhou, Eunah Cho, Xing Fan, Xiaojiang Huang, Yanbin Lu, and Yingzhen Yang",
        "Conference": "arXiv preprint arXiv:2308.14296 (2023)",
        "citation_count": {"value": 97, "date": "2025-01-28 21:46:50"},
    },
    19: {
        "Title": "Intelligent agents: Theory and practice",
        "Author(s)": "Michael Wooldridge and Nicholas R Jennings",
        "Conference": "The knowledge engineering review 10, 2 (1995), 115–152",
        "citation_count": {"value": 11878, "date": "2025-01-28 21:46:54"},
    },
    20: {
        "Title": "Autogen: Enabling next-gen llm applications via multi-agent conversation framework",
        "Author(s)": "Qingyun Wu, Gagan Bansal, Jieyu Zhang, Yiran Wu, Shaokun Zhang, Erkang Zhu, Beibin Li, Li Jiang, Xiaoyun Zhang, and Chi Wang",
        "Conference": "arXiv preprint arXiv:2308.08155 (2023)",
        "citation_count": {"value": 692, "date": "2025-01-28 21:46:57"},
    },
    21: {
        "Title": "React: Synergizing reasoning and acting in language models",
        "Author(s)": "Shunyu Yao, Jeffrey Zhao, Dian Yu, Nan Du, Izhak Shafran, Karthik Narasimhan, and Yuan Cao",
        "Conference": "arXiv preprint arXiv:2210.03629 (2022)",
        "citation_count": {"value": 2096, "date": "2025-01-28 21:46:59"},
    },
    22: {
        "Title": "Glm-130b: An open bilingual pre-trained model",
        "Author(s)": "Aohan Zeng, Xiao Liu, Zhengxiao Du, Zihan Wang, Hanyu Lai, Ming Ding, Zhuoyi Yang, Yifan Xu, Wendi Zheng, Xiao Xia, et al.",
        "Conference": "arXiv preprint arXiv:2210.02414 (2022)",
        "citation_count": {"value": 589, "date": "2025-01-28 21:47:05"},
    },
    23: {
        "Title": "On generative agents in recommendation",
        "Author(s)": "An Zhang, Leheng Sheng, Yuxin Chen, Hao Li, Yang Deng, Xiang Wang, and Tat-Seng Chua",
        "Conference": "arXiv preprint arXiv:2310.10108 (2023)",
        "citation_count": {"value": 91, "date": "2025-01-28 21:47:11"},
    },
    24: {
        "Title": "Building cooperative embodied agents modularly with large language models",
        "Author(s)": "Hongxin Zhang, Weihua Du, Jiaming Shan, Qinhong Zhou, Yilun Du, Joshua B Tenenbaum, Tianmin Shu, and Chuang Gan",
        "Conference": "arXiv preprint arXiv:2307.02485 (2023)",
        "citation_count": {"value": 85, "date": "2025-01-28 21:47:17"},
    },
    25: {
        "Title": "Agentcf: Collaborative learning with autonomous language agents for recommender systems",
        "Author(s)": "Junjie Zhang, Yupeng Hou, Ruobing Xie, Wenqi Sun, Julian McAuley, Wayne Xin Zhao, Leyu Lin, and Ji-Rong Wen",
        "Conference": "arXiv preprint arXiv:2310.09233 (2023)",
        "citation_count": {"value": 55, "date": "2025-01-28 21:47:24"},
    },
}


def index(request):
    # 데이터를 JavaScript에서 사용하기 위해 JSON 형식으로 변환
    paper_list = [
        {
            "id": key,
            "title": paper["Title"],
            "authors": paper["Author(s)"],
            "conference": paper["Conference"],
            "citationCount": paper["citation_count"]["value"],
            "year": (
                int(paper["Conference"].split("(")[-1].split(")")[0])
                if "(" in paper["Conference"]
                else None
            ),
        }
        for key, paper in papers.items()
    ]

    # context로 데이터 전달
    context = {"papers_json": json.dumps(paper_list)}  # JSON으로 변환

    return render(request, "index.html", context)


import os
from django.shortcuts import render
from django.http import JsonResponse


def file_upload_view(request):
    if request.method == "POST":
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file_instance = form.save()
            print(
                {
                    "success": True,
                    "message": "파일 업로드 성공!",
                    "file_id": file_instance.id,  # 업로드된 파일 ID 반환
                    "file_name": file_instance.file.name,
                    "file_url": file_instance.file.url,  # 프론트에서 사용할 URL
                }
            )
            return JsonResponse(
                {
                    "success": True,
                    "message": "파일 업로드 성공!",
                    "file_id": file_instance.id,  # 업로드된 파일 ID 반환
                    "file_name": file_instance.file.name,
                    "file_url": file_instance.file.url,  # 프론트에서 사용할 URL
                }
            )
        else:
            return JsonResponse({"success": False, "errors": form.errors})

    form = FileUploadForm()
    return render(request, "file_upload.html", {"form": form})


def peper_parse_file_view(request, file_id):
    try:
        file_instance = UploadedFile.objects.get(id=file_id)
        file_path = os.path.join(settings.MEDIA_ROOT, file_instance.file.name)
        print(f"file_path : {file_path}")

        KDBAI_TABLE_NAME = "LlamaParse_Table"
        table = rag_parser.db.table(KDBAI_TABLE_NAME)  # 기존 테이블 가져오기

        query = "이 논문의 제목이 뭐야?"
        query_embedding = client.embeddings.create(
            input=query, model="text-embedding-3-small"
        )

        results = table.search(
            vectors={"flat": [query_embedding.data[0].embedding]},
            n=5,
            filter=[("<>", "document_id", "4a9551df-5dec-4410-90bb-43d17d722918")],
        )

        retrieved_data_for_RAG = []
        for index, row in results[0].iterrows():
            retrieved_data_for_RAG.append(row["text"])

        question = (
            "You will answer this question based on the provided reference material: "
            + query
        )
        messages = "Here is the provided context: " + "\n"
        if results:
            for data in retrieved_data_for_RAG:
                messages += data + "\n"
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": question},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": messages},
                    ],
                },
            ],
            # max_tokens=300,
        )
        content = response.choices[0].message.content

        return JsonResponse(
            {
                "success": True,
                "message": "파일 파싱 성공!",
                "file_id": file_id,
                "extracted_text": content[:1000],  # 앞부분 1000자 미리보기
            }
        )
    except UploadedFile.DoesNotExist:
        return JsonResponse({"success": False, "error": "파일을 찾을 수 없습니다."})
    # except Exception as e:
    #     return JsonResponse({"success": False, "error": str(e)})


def source_parse(request):
    print(f"[source_parse]".ljust(60, "-"))
    KDBAI_TABLE_NAME = "LlamaParse_Table"
    table = rag_parser.db.table(KDBAI_TABLE_NAME)  # 기존 테이블 가져오기

    client = OpenAI()

    source_paper_answer = RAG(
        f"""Find this paper's title, authors like example.

EXAMPLE : 
{{
    "from_paper : 
                    {{
                        "title" : "Language models are few-shot learners",
                        "authors" : "Tom Brown, Benjamin Mann, Nick Ryder, Melanie Subbiah, Jared D Kaplan, Prafulla Dhariwal, Arvind Neelakantan, Pranav Shyam, Girish Sastry, Amanda Askell, et al",
                    }}
}}
""",
        table,
        client,
    )
    source_dict = eval(source_paper_answer.replace("```json", "").replace("```", ""))
    print(f"[source_parse]source_dict : \n{source_dict}")

    # 🔹 논문 데이터 추가 (중복 방지)
    added_paper = neo4j_client.add_paper(
        source_dict["from_paper"]["title"], source_dict["from_paper"]["authors"]
    )
    print("[source_parse]Added Paper:", added_paper)

    return JsonResponse({"success": True, "source_dict": source_dict})


@csrf_exempt
def reference_parse(request):
    print(f"[reference_parse]".ljust(60, "-"))
    KDBAI_TABLE_NAME = "LlamaParse_Table"
    table = rag_parser.db.table(KDBAI_TABLE_NAME)  # 기존 테이블 가져오기

    client = OpenAI()
    print(f"[reference_parse] RAG ing..")

    def stream_references():
        #     ref_parse_answer = RAG(
        #         f"""Find this paper's References. Give me that References with the given json form. Don't return any other comments except that References

        # EXAMPLE :
        # {{
        #     1 : {{
        #             "from_paper :
        #                             {{
        #                                 "title" : "Language models are few-shot learners",
        #                                 "authors" : "Tom Brown, Benjamin Mann, Nick Ryder, Melanie Subbiah, Jared D Kaplan, Prafulla Dhariwal, Arvind Neelakantan, Pranav Shyam, Girish Sastry, Amanda Askell, et al",
        #                                 "source" : "Advances in neural information processing systems 33 (2020), 1877–1901",
        #                                 "year" : 2020
        #                             }}
        #     }},
        #     2 : {{
        #         ...
        #     }},
        #     ...
        # }}
        # """,
        #         table,
        #         client,
        #     )
        #     ref_dict = eval(ref_parse_answer.replace("```json", "").replace("```", ""))

        ref_dict = {
            1: {
                "from_paper": {
                    "title": "Language models are few-shot learners",
                    "authors": "Tom Brown, Benjamin Mann, Nick Ryder, Melanie Subbiah, Jared D Kaplan, Prafulla Dhariwal, Arvind Neelakantan, Pranav Shyam, Girish Sastry, Amanda Askell, et al.",
                    "source": "Advances in neural information processing systems 33 (2020), 1877–1901",
                    "year": 2020,
                },
                "from_scholarly": {
                    "title": "Language models are few-shot learners",
                    "authors": "T Brown, B Mann, N Ryder",
                    "citation_count": {"value": 39745, "date": "2025-02-07 17:09:12"},
                },
            },
            2: {
                "from_paper": {
                    "title": "Trends in distributed artificial intelligence",
                    "authors": "Brahim Chaib-Draa, Bernard Moulin, René Mandiau, and Patrick Millot",
                    "source": "Artificial Intelligence Review 6 (1992), 35–66",
                    "year": 1992,
                },
                "from_request": {
                    "title": "Trends in distributed artificial intelligence",
                    "authors": "B Chaib-Draa, B Moulin, R Mandiau, P Millot",
                    "citation_count": {"value": 282, "date": "2025-02-07 17:09:18"},
                },
            },
            3: {
                "from_paper": {
                    "title": "Agentverse: Facilitating multi-agent collaboration and exploring emergent behaviors in agents",
                    "authors": "Weize Chen, Yusheng Su, Jingwei Zuo, Cheng Yang, Chenfei Yuan, Chen Qian, Chi-Min Chan, Yujia Qin, Yaxi Lu, Ruobing Xie, et al.",
                    "source": "arXiv preprint arXiv:2308.10848 (2023)",
                    "year": 2023,
                },
                "from_scholarly": {
                    "title": "Agentverse: Facilitating multi-agent collaboration and exploring emergent behaviors in agents",
                    "authors": "W Chen, Y Su, J Zuo, C Yang",
                    "citation_count": {"value": 159, "date": "2025-02-07 17:09:21"},
                },
            },
            4: {
                "from_paper": {
                    "title": "Improving Factuality and Reasoning in Language Models through Multiagent Debate",
                    "authors": "Yilun Du, Shuang Li, Antonio Torralba, Joshua B Tenenbaum, and Igor Mordatch",
                    "source": "arXiv preprint arXiv:2305.14325 (2023)",
                    "year": 2023,
                },
                "from_scholarly": {
                    "title": "Improving factuality and reasoning in language models through multiagent debate",
                    "authors": "Y Du, S Li, A Torralba, JB Tenenbaum",
                    "citation_count": {"value": 460, "date": "2025-02-07 17:09:24"},
                },
            },
        }

        print(f"ref_dict 추출 완료")

        # 🔹 실시간으로 데이터 응답 (스트리밍)
        for i, one_ref_info in ref_dict.items():
            # ref_paper_title = one_ref_info["from_paper"]["title"]
            # ref_paper_authors = one_ref_info["from_paper"]["authors"]
            # ref_paper_source = one_ref_info["from_paper"]["source"]

            # print(f"{i}/{len(ref_dict)}".ljust(120, "-"))
            # print(f"ref_paper_title : {ref_paper_title}")
            # print(f"ref_paper_authors : {ref_paper_authors}")
            # print(f"ref_paper_source : {ref_paper_source}")

            # scholary_result = get_citation_count_using_scholarly(
            #     ref_paper_title, ref_paper_authors, ref_paper_source
            # )

            # if scholary_result is not None:
            #     ref_dict[i]["from_scholarly"] = scholary_result
            # else:
            #     request_result = get_citation_count_using_request(
            #         ref_paper_title, ref_paper_authors
            #     )
            #     if request_result is not None:
            #         ref_dict[i]["from_request"] = request_result
            # if "from_scholarly" in ref_dict[i]:
            #     print(f"from_scholarly : ")
            #     print(ref_dict[i]["from_scholarly"])
            # if "from_request" in ref_dict[i]:
            #     print(f"from_request : ")
            #     print(ref_dict[i]["from_request"])

            if (
                "from_scholarly" in one_ref_info
                and one_ref_info["from_scholarly"].get("citation_count", {}).get("value")
                is not None
            ) or (
                "from_request" in one_ref_info
                and one_ref_info["from_request"].get("citation_count", {}).get("value")
                is not None
            ):
                json_data = json.dumps({"one_ref_info": one_ref_info})
                print(f"✅ 전송할 데이터: {json_data}")
                yield f"data: {json_data}\n\n"
                time.sleep(1)  # 🔹 JS에서 차례로 추가되도록 살짝 지연

    response = StreamingHttpResponse(
        stream_references(), content_type="text/event-stream"
    )
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"  # Nginx 사용 시 버퍼링 방지
    return response
    # return JsonResponse({"success": True, "source_dict": ref_dict})
