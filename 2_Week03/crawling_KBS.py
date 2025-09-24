"""
crawling_KBS.py
- KBS 헤드라인 크롤링 (강화판)
    폴백 순서: KBS RSS → JSON-LD → DOM → Google News RSS(site:news.kbs.co.kr)
- 보너스: KOSPI 지수, 날씨(Seoul)
- 특징: 세션 재시도, 강한 UA/헤더, 디버그 로그
"""

from __future__ import annotations
import json
import re
import sys
import xml.etree.ElementTree as ET
from typing import List, Optional, Iterable

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# bs4는 있으면 사용
try:
    from bs4 import BeautifulSoup  # type: ignore
    HAS_BS4 = True
except Exception:
    HAS_BS4 = False

DEBUG = False  # 문제 생기면 True로 바꿔 실행하면 경로/상태 출력됨

KBS_HOME = "https://news.kbs.co.kr"
GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q=site:news.kbs.co.kr&hl=ko&gl=KR&ceid=KR:ko"

# -------------------------
# 요청 세션(재시도/헤더)
# -------------------------

def build_session() -> requests.Session:
    s = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=0.4,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET", "HEAD"),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retries, pool_connections=10, pool_maxsize=10)
    s.mount("http://", adapter)
    s.mount("https://", adapter)
    s.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive",
    })
    return s

SESSION = build_session()

def get(url: str, timeout: int = 10) -> requests.Response:
    # 일부 사이트는 Referer 없으면 막기도 해서 가볍게 추가
    headers = {"Referer": KBS_HOME}
    r = SESSION.get(url, headers=headers, timeout=timeout)
    # 인코딩 추정 보정
    if not r.encoding or r.encoding.lower() == "iso-8859-1":
        r.encoding = r.apparent_encoding or "utf-8"
    r.raise_for_status()
    return r

# -------------------------
# 유틸
# -------------------------

def clean_text(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()

def unique_keeping_order(items: Iterable[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for it in items:
        if it not in seen:
            seen.add(it)
            out.append(it)
    return out

# -------------------------
# KBS 헤드라인 크롤러
# -------------------------

class KbsHeadlines:
    """
    헤드라인 폴백 체인:
    1) KBS RSS (여러 엔드포인트 순회)
    2) JSON-LD <script type="application/ld+json"> 의 "headline"
    3) DOM에서 a[href] 패턴
    4) Google News RSS (site:news.kbs.co.kr)
    """

    RSS_CANDIDATES = [
        # 존재 여부가 수시로 바뀔 수 있으니 전부 시도
        "https://news.kbs.co.kr/rss/news_main.xml",
        "https://news.kbs.co.kr/rss/news.xml",
        "https://news.kbs.co.kr/rss/newsall.xml",
        # 섹션
        "https://news.kbs.co.kr/rss/politics.xml",
        "https://news.kbs.co.kr/rss/economy.xml",
        "https://news.kbs.co.kr/rss/society.xml",
        "https://news.kbs.co.kr/rss/international.xml",
        "https://news.kbs.co.kr/rss/culture.xml",
        "https://news.kbs.co.kr/rss/it.xml",
    ]

    def fetch(self, limit: int = 30) -> List[str]:
        # 1) RSS
        titles = self._from_rss(limit)
        if titles:
            if DEBUG: print("[DEBUG] KBS RSS 성공")
            return titles

        # 2) JSON-LD
        try:
            html = get(KBS_HOME).text
        except Exception as e:
            if DEBUG: print(f"[DEBUG] KBS 메인 GET 실패: {e}")
            html = ""

        if html:
            titles = self._from_jsonld(html, limit)
            if titles:
                if DEBUG: print("[DEBUG] JSON-LD 성공")
                return titles

            # 3) DOM
            titles = self._from_dom(html, limit)
            if titles:
                if DEBUG: print("[DEBUG] DOM 성공")
                return titles

        # 4) Google News RSS (KBS 출처만)
        titles = self._from_google_news(limit)
        if titles:
            if DEBUG: print("[DEBUG] Google News RSS 성공")
            return titles

        return []

    # ---------- 1) KBS RSS ----------
    def _from_rss(self, limit: int) -> List[str]:
        for rss_url in self.RSS_CANDIDATES:
            try:
                r = get(rss_url, timeout=8)
                if DEBUG: print(f"[DEBUG] RSS 상태 {rss_url}: {r.status_code}, {len(r.text)} bytes")
                xml_txt = r.text
                if "<rss" not in xml_txt and "<feed" not in xml_txt:
                    continue
                titles = self._parse_rss_titles(xml_txt, limit)
                if titles:
                    return titles
            except Exception as e:
                if DEBUG: print(f"[DEBUG] RSS 실패 {rss_url}: {e}")
                continue
        return []

    @staticmethod
    def _parse_rss_titles(xml_txt: str, limit: int) -> List[str]:
        try:
            root = ET.fromstring(xml_txt)
        except Exception:
            return []
        out: List[str] = []

        # RSS 2.0
        for it in root.findall(".//item"):
            t = clean_text(it.findtext("title") or "")
            if t:
                out.append(t)
            if len(out) >= limit:
                break

        # Atom (백업)
        if not out:
            for it in root.findall(".//{*}entry"):
                t = clean_text(it.findtext("{*}title") or "")
                if t:
                    out.append(t)
                if len(out) >= limit:
                    break

        out = [t for t in out if 5 <= len(t) <= 200]
        return unique_keeping_order(out)[:limit]

    # ---------- 2) JSON-LD ----------
    def _from_jsonld(self, html: str, limit: int) -> List[str]:
        out: List[str] = []

        # <script type="application/ld+json">를 모두 수집
        script_blocks = re.findall(
            r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
            html, flags=re.DOTALL | re.IGNORECASE
        )

        for block in script_blocks:
            block = block.strip()
            # JSON 파싱이 가능한 경우만 시도
            try:
                data = json.loads(block)
            except Exception:
                # 배열로 싸여있는 형태일 수 있으니 느슨하게 보정
                try:
                    # 끝에 콤마 등 깨진 경우 제거
                    block2 = block.strip()
                    data = json.loads(block2)
                except Exception:
                    continue

            def collect_from(obj):
                if isinstance(obj, dict):
                    if "headline" in obj and isinstance(obj["headline"], str):
                        t = clean_text(obj["headline"])
                        if self._looks_like_title(t):
                            out.append(t)
                    for v in obj.values():
                        collect_from(v)
                elif isinstance(obj, list):
                    for v in obj:
                        collect_from(v)

            collect_from(data)

            if len(out) >= limit:
                break

        return unique_keeping_order(out)[:limit]

    # ---------- 3) DOM ----------
    def _from_dom(self, html: str, limit: int) -> List[str]:
        candidates: List[str] = []

        if HAS_BS4:
            soup = BeautifulSoup(html, "html.parser")

            # 상세기사 패턴
            for a in soup.select('a[href*="/news/view.do"]'):
                txt = clean_text(a.get_text(" "))
                if self._looks_like_title(txt):
                    candidates.append(txt)

            # 일반 뉴스 경로
            if len(candidates) < limit:
                for a in soup.select('a[href^="/news/"]'):
                    txt = clean_text(a.get_text(" "))
                    if self._looks_like_title(txt):
                        candidates.append(txt)

            # 헤딩 내부
            if len(candidates) < limit:
                for h in soup.select("h1 a, h2 a, h3 a, h4 a"):
                    txt = clean_text(h.get_text(" "))
                    if self._looks_like_title(txt):
                        candidates.append(txt)
        else:
            # 정규식 폴백(간단)
            pattern = re.compile(
                r'<a\b[^>]*href="(?P<href>[^"]+)"[^>]*>(?P<text>.*?)</a>',
                re.IGNORECASE | re.DOTALL,
            )
            for m in pattern.finditer(html):
                href = m.group("href")
                text = clean_text(re.sub("<[^>]+>", " ", m.group("text")))
                if not text:
                    continue
                if "/news/view.do" in href and self._looks_like_title(text):
                    candidates.append(text)
                elif href.startswith("/news/") and self._looks_like_title(text):
                    candidates.append(text)

        titles = [t for t in candidates if 8 <= len(t) <= 120]
        return unique_keeping_order(titles)[:limit]

    # ---------- 4) Google News RSS ----------
    def _from_google_news(self, limit: int) -> List[str]:
        try:
            r = get(GOOGLE_NEWS_RSS, timeout=8)
            if DEBUG:
                print(f"[DEBUG] Google News RSS 상태: {r.status_code}, {len(r.text)} bytes")
            xml_txt = r.text
            return self._parse_rss_titles(xml_txt, limit)
        except Exception as e:
            if DEBUG: print(f"[DEBUG] Google News RSS 실패: {e}")
            return []

    @staticmethod
    def _looks_like_title(s: str) -> bool:
        bad = ("더보기", "바로가기", "영상", "동영상", "구독", "로그인", "공지")
        return len(s) >= 8 and not any(b in s for b in bad)

# -------------------------
# KOSPI · 날씨
# -------------------------

def fetch_kospi() -> Optional[str]:
    url = "https://finance.naver.com/sise/sise_index.naver?code=KOSPI"
    html = get(url).text

    m = re.search(r'id=["\']now_value["\']\s*>\s*([\d,]+\.\d+|\d[\d,]*)\s*<', html)
    if m:
        return m.group(1)

    near = re.search(r"(?:현재가|지수)\s*</[^>]+>\s*<[^>]+>\s*([\d,]+\.\d+|\d[\d,]*)", html)
    if near:
        return near.group(1)

    nums = re.findall(r">([\d,]+\.\d+|\d[\d,]*)<", html)
    if nums:
        nums.sort(key=lambda x: (x.count(","), len(x), x), reverse=True)
        return nums[0]
    return None

def fetch_weather(city: str = "Seoul") -> Optional[dict]:
    url = f"https://wttr.in/{city}?format=j1"
    try:
        r = get(url, timeout=10)
        data = r.json()
        current = data.get("current_condition", [{}])[0]
        return {
            "city": city,
            "temp_C": current.get("temp_C"),
            "feels_like_C": current.get("FeelsLikeC"),
            "weather_desc": (current.get("weatherDesc", [{}])[0].get("value")),
            "humidity": current.get("humidity"),
        }
    except Exception:
        return None

# -------------------------
# 메인
# -------------------------

def main() -> None:
    crawler = KbsHeadlines()
    try:
        headlines = crawler.fetch(limit=30)
    except Exception as e:
        if DEBUG: print("[DEBUG] 전체 fetch 예외:", e, file=sys.stderr)
        headlines = []

    print("=== KBS 헤드라인 ===")
    if headlines:
        for i, t in enumerate(headlines, 1):
            print(f"{i:02d}. {t}")
    else:
        print("수집 실패(구조 변경, 접근 차단, 또는 네트워크 문제 가능).")
        if not DEBUG:
            print("└ 디버그를 켜려면 파일 상단 DEBUG=True 로 바꿔 실행해 원인 로그를 보세요.")

    print("\n=== KOSPI 지수 ===")
    try:
        kospi = fetch_kospi()
        print(kospi if kospi else "가져오기 실패")
    except Exception as e:
        print("[KOSPI] 오류:", e, file=sys.stderr)
        print("가져오기 실패")

    print("\n=== 날씨(Seoul) ===")
    try:
        w = fetch_weather("Seoul")
        if w:
            print(f"{w['city']}: {w['temp_C']}°C (체감 {w['feels_like_C']}°C), "
                f"{w['weather_desc']}, 습도 {w['humidity']}%")
        else:
            print("가져오기 실패")
    except Exception as e:
        print("[Weather] 오류:", e, file=sys.stderr)
        print("가져오기 실패")

if __name__ == "__main__":
    main()
