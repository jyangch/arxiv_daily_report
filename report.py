import os
import pytz
import arxiv
import datetime
from google import genai
from openai import OpenAI
from datetime import timedelta


PREFERRED_PROVIDER = "gemini"  # "gemini" or "openai"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite-preview")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.4")

gemini_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


def get_arxiv_sync_window():
    
    tz_et = pytz.timezone('US/Eastern')
    now_et = datetime.datetime.now(tz_et)

    weekday = now_et.weekday() 
    if weekday == 0:
        days_back = 3
    elif weekday in [5, 6]:
        days_back = 0
    else:
        days_back = 1

    end_time = now_et.replace(hour=14, minute=0, second=0, microsecond=0) - timedelta(days=1)
    start_time = end_time - timedelta(days=days_back)
    
    return start_time, end_time


def fetch_arxiv_papers():
    
    start_t, end_t = get_arxiv_sync_window()
    print(f"🔍 Fetching arXiv announcements (Submission window: {start_t} -> {end_t} ET)")

    arxiv_client = arxiv.Client()
    search = arxiv.Search(query="cat:astro-ph.he", max_results=100, sort_by=arxiv.SortCriterion.SubmittedDate)
    
    papers = []
    for r in arxiv_client.results(search):
        pub_et = r.published.astimezone(pytz.timezone('US/Eastern'))
        if start_t <= pub_et < end_t:
            papers.append({
                "title": r.title,
                "authors": ", ".join([a.name for a in r.authors]),
                "summary": r.summary,
                "url": r.entry_id,
                "pdf_url": r.pdf_url,
                "categories": r.categories
            })
    
    print(f"✅ Found {len(papers)} papers submitted within the sync window.")
    
    return papers


def _is_quota_error(error):
    
    msg = str(error).lower()
    
    return ("429" in msg) or ("resource_exhausted" in msg) or ("quota exceeded" in msg)


def _generate_with_gemini(prompt):
    
    if not gemini_client:
        raise RuntimeError("Gemini API key is missing. Set GEMINI_API_KEY.")
    response = gemini_client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
    )
    
    return response.text


def _generate_with_openai(prompt):
    
    if not openai_client:
        raise RuntimeError("OpenAI API key is missing. Set OPENAI_API_KEY.")
    response = openai_client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content


def generate_report(papers):
    
    if not papers: 
        return "No new papers today.</p>", ""
    
    input_text = ""
    for i, p in enumerate(papers):
        input_text += (
            f"[{i+1}] Entry ID: {p['url']}\n"
            f"Title: {p['title']}\n"
            f"Authors: {p['authors']}\n"
            f"Categories: {', '.join(p['categories'])}\n"
            f"Abstract: {p['summary']}\n\n"
        )

    prompt = f"""
    你是一名资深天文学家。请仔细阅读以下 {len(papers)} 篇论文，严格按以下格式输出 HTML:

    一、领域归类 (Index Section)
    按领域（如：伽马射线暴、超新星、宇宙射线、黑洞等）分类，在每个类别后列出对应的论文编号。
    格式示例：伽马射线暴：[1], [5]。编号超链接至论文条目中的编号。

    二、论文条目 (Details Section)
    按编号顺序排列所有 {len(papers)} 篇论文。每篇论文严格按照以下格式：
    [编号] 带有链接的Entry ID。示例: [1]: https://arxiv.org/abs/xxxx.xxxxx
    英文标题：英文标题。
    中文标题：中文标题（请翻译英文标题，保持学术严谨）
    作者：原始作者姓名。如果作者数量超过 10 位，超过部分显示为 "et al."。示例: A. Einstein, N. Bohr, M. Curie, et al.
    研究方法：需判定为 [Observation] / [Simulation] / [Theory] / [Modeling] 之一。请直接描述核心方法，使用 2-3 句地道的中文学术表达。保留希腊字母和物理符号。
    物理结果：严禁使用‘本文研究了...’这种废话。请直接描述物理发现，使用 2-3 句地道的中文学术表达。保留希腊字母和物理符号。

    要求：
    - 严禁使用 Markdown 符号（如 ##, **），必须使用纯 HTML 标签 (<h3>, <ul>, <li>, <p>, <strong>)。
    - 只返回 <body> 内部内容。

    待处理论文：
    {input_text}
    """

    providers = [PREFERRED_PROVIDER, "openai" if PREFERRED_PROVIDER == "gemini" else "gemini"]
    print(f"🧠 Preferred provider: {providers[0]}. Generating report...")

    last_error = None
    for provider in providers:
        try:
            if provider == "gemini":
                print("   Trying Gemini...")
                return _generate_with_gemini(prompt), provider
            
            else:
                print("   Trying OpenAI...")
                return _generate_with_openai(prompt), provider
        except Exception as e:
            last_error = e
            if _is_quota_error(e):
                next_provider = "openai" if provider == "gemini" else "gemini"
                print(f"⚠️ {provider} quota/rate limit hit, falling back to {next_provider}. Details: {e}")
                continue
            print(f"⚠️ {provider} failed: {e}")

    raise RuntimeError(f"All providers failed. Last error: {last_error}")


def save_html(papers, report, provider):
    
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    html_layout = f"""
    <!DOCTYPE html>
    <html lang="zh">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: "Microsoft YaHei", "微软雅黑", "PingFang SC", sans-serif; color: #333; max-width: 900px; margin: auto; padding: 20px; }}
        body, p, li {{ line-height: 1.4; }}
        .header {{ background: #004085; color: white; padding: 20px; border-radius: 10px; text-align: center; }}
        .index-box {{ background: #f8f9fa; border: 1px solid #dee2e6; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .paper-item {{ border-bottom: 1px solid #eee; padding: 15px 0; }}
        .method-tag {{ color: #28a745; font-weight: bold; font-size: 0.9em; }}
        h3 {{ color: #004085; border-left: 5px solid #004085; padding-left: 10px; margin-top: 40px; }}
    </style>
    </head>
    <body>
    <div class="header">
        <h2 style="margin:0;">高能天体物理文章日报</h2>
        <p>{date_str} | 今日同步更新{len(papers)}篇 | By {provider}</p>
    </div>
    {report.replace('```html', '').replace('```', '')}
    </body>
    </html>"""
    
    filename = f"./reports/arXiv_astro_ph_HE_daily_report_{date_str}.html"
    with open(filename, "w", encoding="utf-8-sig") as f:
        f.write(html_layout)
    print(f"✨ Sync version of daily report (Index + Details) generated: {filename}")


if __name__ == "__main__":
    papers = fetch_arxiv_papers()
    try:
        report, provider = generate_report(papers)
    except Exception as error:
        print(f"❌ Report generation failed: {error}")
        raise SystemExit(1)

    save_html(papers, report, provider)