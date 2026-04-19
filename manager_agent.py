import os
import datetime
from duckduckgo_search import DDGS
from google import genai
import json

def fetch_specific_news():
    """使用 DuckDuckGo 針對使用者指定的新聞來源進行精準搜尋"""
    print("[1/3] Fetching targeted market news from specific sources...")
    now = datetime.datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    current_month_str = now.strftime("%Y年%m月")
    
    # 建立指定來源的搜尋條件
    us_sources = "site:bloomberg.com OR site:reuters.com OR site:wsj.com OR site:cnbc.com OR site:ft.com OR site:seekingalpha.com OR site:fool.com"
    hk_sources = "site:aastocks.com OR site:hket.com OR site:futunn.com OR site:finance.sina.com.cn OR site:gelonghui.com OR site:xueqiu.com OR site:zhitongcaijing.com"
    
    queries = {
        "美股與宏觀重點": f"{us_sources} market news finance economy {today_str}",
        "港股與A股重點": f"{hk_sources} 股市 財經新聞 重點 {today_str}",
        "重要經濟數據與會議": f"site:investing.com OR site:hkma.gov.hk {current_month_str} 經濟數據 會議",
        "業績公佈前瞻": f"site:investing.com OR site:aastocks.com {current_month_str} 美股 港股 業績 公佈"
    }

    raw_data = ""
    try:
        with DDGS() as ddgs:
            for category, query in queries.items():
                print(f"  -> 搜尋分類: {category}")
                # 採用最近一天的搜尋結果(新聞時效性)
                results = list(ddgs.text(query, max_results=8, timelimit='w'))
                raw_data += f"\n=== 【{category}】 ===\n"
                for res in results:
                    raw_data += f"- [{res.get('title')}]({res.get('href')}): {res.get('body')}\n"
    except Exception as e:
        print(f"Warning: News fetch failed: {e}")
        raw_data += "\nWarning: Unable to fetch live news, please use general market analysis."

    return raw_data

def generate_report(news_data):
    """Use Gemini AI to generate a highly professional HTML report"""
    print("[2/3] Generating professional HTML report with Gemini AI...")
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found. Please set the environment variable.")
        # 回傳一個預設錯誤網頁
        return "<html><body><h1>請先設定 GEMINI_API_KEY 環境變數 (GitHub Secrets)</h1></body></html>"

    client = genai.Client(api_key=api_key)
    today_date = datetime.datetime.now().strftime('%Y年%m月%d日 %H:%M')

    prompt = f"""
    你是一位華爾街頂尖的專業投資基金經理，你的任務是從以下以特定來源抓取到的新聞資料庫中，提煉並產出一份每日 09:00 發布的【專屬每日投資建議報告】。

    你必須輸出完全符合格式的 HTML 程式碼（包含現代化、金融科技質感的內聯 CSS 美化），不需要任何 Markdown 標記，確保網頁可以直接作為網站首頁運行！

    【報告設計與內容要求】：
    1. **主題風格 (Aesthetics)**：以專業量化基金的 Dark Mode 或深藍質感風格為主，擁有漂亮乾淨的漸層背景、陰影和圓角。
    2. **標題區塊**：顯眼的專屬標題「專業投資基金經理每日報告」，副標題包含時間 ({today_date})。
    3. **Part A: 今日最新重點財經新聞 (美股及港股)**
       - 將新聞分為「🇺🇸美股及全球宏觀」與「🇭🇰港股/A股及亞洲市場」。
       - 分析新聞來源提供的重點，給出市場情緒判斷。
    4. **Part B: 經濟數據 / 重要會議及內容**
       - 使用精美的 HTML 表格 (Table) 列出即將發生或剛發布的重點數據與會議，必須包含「時間」、「地區」、「事件」與「市場影響預期」。
    5. **Part C: 2026年4月/當月 港股及美股重點業績前瞻**
       - 列表點出即將公布財報的核心公司與關注重點。
    6. **Part D: 基金經理操作建議 (Actionable Advice)**
       - 提供一個突出的「高光區塊 (Highlight Block)」給出最具價值的實質操作建議（例如短線避險、板塊輪動建議等）。

    【輸入原始資料】(包含 Bloomberg, WSJ, CNBC, Reuters, 富途, 阿思達克等搜尋結果摘要)：
    {news_data}
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-pro', # 使用 Pro 模型以獲得最高品質的分析與高品質 HTML 排版
            contents=prompt,
        )
        html_content = response.text
        # Clean markdown wrappers if returned
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
    print("--- Fund Manager Automator Started ---")
    try:
        news_data = fetch_specific_news()
        html_report = generate_report(news_data)
        save_path = save_report(html_report)
        return save_path
    except Exception as e:
        print(f"Error during job execution: {e}")

if __name__ == "__main__":
    run_task()
