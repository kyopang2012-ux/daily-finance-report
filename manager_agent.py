import os
import datetime
from duckduckgo_search import DDGS
from google import genai

def fetch_specific_news():
    """使用 DuckDuckGo 針對使用者指定的所有新聞來源進行廣泛精準搜尋"""
    print("[1/3] Fetching targeted market news from specific sources...")
    now = datetime.datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    current_month_str = now.strftime("%Y年%m月")
    
    # 全球/美股來源
    us_sources = "site:bloomberg.com OR site:reuters.com OR site:wsj.com OR site:cnbc.com OR site:ft.com OR site:seekingalpha.com OR site:fool.com"
    # 港股/A股來源
    hk_sources = "site:aastocks.com OR site:hket.com OR site:futunn.com OR site:finance.sina.com.cn OR site:gelonghui.com OR site:xueqiu.com OR site:zhitongcaijing.com"
    
    queries = {
        "全球與美股新聞": f"{us_sources} market news finance economy {today_str}",
        "港股與A股新聞": f"{hk_sources} 股市 財經新聞 {today_str}",
        "經濟數據與會議": f"site:investing.com OR site:cnbc.com OR site:hket.com {today_str} 經濟數據 會議 議息",
        "本月業績公佈": f"site:investing.com OR site:aastocks.com {current_month_str} 美股 港股 業績 財報 公佈"
    }

    raw_data = ""
    try:
        with DDGS() as ddgs:
            for category, query in queries.items():
                print(f"  -> 搜尋分類: {category}")
                # 提高抓取數量至 12 筆，以確保覆蓋所有指定媒體
                results = list(ddgs.text(query, max_results=12, timelimit='w'))
                raw_data += f"\n=== 【{category}】 ===\n"
                for res in results:
                    raw_data += f"- 來源/標題: [{res.get('title')}]({res.get('href')}): {res.get('body')}\n"
    except Exception as e:
        print(f"Warning: News fetch failed: {e}")
        raw_data += "\nWarning: Unable to fetch live news, please use general market analysis."

    return raw_data

def generate_report(news_data):
    """Use Gemini AI to generate a highly professional HTML report matching specific criteria A-D"""
    print("[2/3] Generating professional HTML report with Gemini AI...")
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found. Please set the environment variable.")
        return "<html><body><h1>請先設定 GEMINI_API_KEY 環境變數 (GitHub Secrets)</h1></body></html>"

    client = genai.Client(api_key=api_key)
    today_date = datetime.datetime.now().strftime('%Y年%m月%d日')

    prompt = f"""
    你是一位華爾街頂尖的專業投資基金經理，任務是根據以下從特定來源抓取的市場消息，產出一份【專屬每日投資建議報告】。
    
    你必須輸出完全符合格式的 HTML 程式碼（包含現代化、深藍漸層質感、無邊框設計的內聯 CSS 美化），不需要 Markdown 標記，網頁需直接可用。

    【核心報告指令 - 必須嚴格包含以下 A 到 D 四個區塊】：
    
    標題區塊：顯示「專業投資基金經理每日報告 - {today_date}」。
    
    區塊 A. 詳細搜尋今天最新重點財經新聞
    - 根據抓取的資料，寫出一篇深入的今日市場總結與分析，包含市場情緒與宏觀經濟概述。

    區塊 B. 詳列明今天最新重點財經新聞 / 經濟數據 / 重要會議及內容 (港股及美股)
    - 以精美的 HTML 表格 (Table) 呈現。
    - 表格欄位必須包含：「時間」、「市場 (美股/港股)」、「新聞/數據/會議內容」、「影響(基金經理點評)」。
    - 將抓取到的重大新聞、數據與會議條列於此。

    區塊 C. 詳細搜尋 {today_date[:7]} 所有港股及美股業績
    - 條列出即將公布業績的重點公司（美股與港股），並點評其市場預期。

    區塊 D. 重點新聞來源追蹤與操作建議
    - 列出今日對市場造成最大影響的新聞來源媒體（必須從 Bloomberg, Reuters, WSJ, CNBC, FT, AAStocks, HKET, 富途, 雪球, 新浪, 智通財經 中挑選提及）。
    - 基金經理人給出的具體、可執行的今日操作策略與避險建議 (Actionable Advice)。

    【輸入原始資料】(即時抓取的媒體資料庫)：
    {news_data}
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash', # 維持使用免費最新穩定版
            contents=prompt,
        )
        html_content = response.text
        if html_content.strip().startswith("```html"):
            html_content = html_content.strip().split("```html", 1)[1]
        if html_content.strip().endswith("```"):
            html_content = html_content.strip().rsplit("```", 1)[0]
        return html_content.strip()
    except Exception as e:
        print(f"Error calling Gemini AI: {e}")
        return "<html><body><h1>Error generating report from Gemini AI.</h1></body></html>"

def save_report(html_content):
    """Save the HTML content to index.html for GitHub Pages."""
    print("[3/3] Saving final index.html report...")
    workspace_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(workspace_dir, "index.html")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Success! Report saved to: {file_path}")
    return file_path

def run_task():
    print("--- Fund Manager Automator Expanded Version Started ---")
    try:
        news_data = fetch_specific_news()
        html_report = generate_report(news_data)
        save_path = save_report(html_report)
        return save_path
    except Exception as e:
        print(f"Error during job execution: {e}")

if __name__ == "__main__":
    run_task()
