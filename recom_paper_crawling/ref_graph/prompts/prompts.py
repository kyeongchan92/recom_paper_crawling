PAPER_COMPARE_PROMPT = """🔹 Task Instruction
Determine whether A paper and B paper refer to the same research work. If they do, respond with "YES"; otherwise, respond with "NO".

When making this judgment, apply the following considerations:

🔹 Considerations for Matching Papers
1. Title Matching (Minor Differences Allowed)
✅ Match the papers even if:

The capitalization, punctuation, or spacing is slightly different.
Example: "GPT-4 Technical Report" vs. "Gpt-4 technical report" → Match
There are minor wording differences that do not change the meaning.
Example: "Large-scale language model society" vs. "Large language model society" → Match
🚨 Do NOT match the papers if:

The core meaning of the title is different.
Example: "GPT-4 Overview" vs. "GPT-3.5 Architecture" → Not the same paper
2. Source Matching (Preprints, Conferences, Journals, DOI, URLs)
✅ Match the papers even if:

One is an arXiv preprint, and the other is a published conference/journal version of the same research.
Example: arXiv preprint arXiv:2303.17760 → NeurIPS 2023 proceedings link → Same research work
The URLs are different but point to the same DOI, arXiv ID, or official publisher repository.
Example:
"https://arxiv.org/abs/2303.08774"
"https://proceedings.neurips.cc/.../2303.08774"
→ Same paper
The conference/journal version is an extended version of an arXiv paper, unless there is major content divergence.
🚨 Do NOT match the papers if:

The DOI/arXiv ID is different, and there is no indication that one is a revision of the other.
One is from a completely different publisher (e.g., IEEE vs. ACL Anthology) without a clear link between them.
3. Author Name Variations (Abbreviations & Institutional Naming Allowed)
✅ Match the papers even if:

Authors use initials instead of full names.
Example: "Guohao Li" vs. "G Li" → Same author
Authors are listed differently between an arXiv preprint and a published paper.
Example: "OpenAI" vs. "J Achiam, S Adler, S Agarwal" → Match if source matches
A company name is used instead of individual authors.
🚨 Do NOT match the papers if:

A completely different research group is listed.
The list of authors has no significant overlap.
4. Edition or Version Differences (Preprint vs. Published Paper)
✅ Match the papers even if:

One version is an early preprint and the other is a peer-reviewed conference/journal version.
The published version contains minor updates or additional experiments but is still based on the same research.
🚨 Do NOT match the papers if:

The newer version substantially changes the research (e.g., different methodology, new experiments, different conclusions).
The preprint was not accepted by the listed conference/journal.

A paper title : {a_paper_title}
A paper authors : {a_paper_authors}
A paper source : {a_paper_source}

B paper title : {b_paper_title}
B paper authors : {b_paper_authors}
B paper source : {b_paper_source}"""


REQUEST_HTML_PARSING_PROMPT = """Parse the given HTML code like the given format. Never answer the other comments but formatted information.

HTML : {one_paper_box_html}

Format example :
{{
    "title" : "Language models are few-shot learners",
    "authors" : "T Brown, B Mann, N Ryder",
    "citation_count" : 39209,
    "link_description" : ""
}}"""

REQUEST_REAL_CITATION_PROMPT = """What is the real citation count of the below paper title and authors?
- Return with given format using only Candidates' information.
- If an exact match for the paper cannot be found in Candidates, say only 'NO'.

### The paper whose citation count I want to know
paper title : {ref_paper_title}
paper authors : {ref_paper_authors}

### Candidates
{request_box_collect}

### Return Format
{{
    "title" : ,
    "authors" : ,
    "citation_count" : {{
                        'value' : citation_count,
                        }}
}}"""
