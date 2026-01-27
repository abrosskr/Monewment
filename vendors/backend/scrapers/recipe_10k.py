# app/scrapers/recipe_10k.py
"""
만개의 레시피 스크래퍼 - 크롤링 차단 우회 전략 포함
"""
import requests
from bs4 import BeautifulSoup
import time
import random
from typing import Optional, Dict, List

class Recipe10kScraper:
    BASE_URL = "https://www.10000recipe.com/recipe/list.html"
    
    # 다양한 User-Agent 로테이션 (차단 우회 전략 #1)
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]
    
    def __init__(self):
        self.session = requests.Session()
        self._request_count = 0
        self._last_request_time = 0
        
    def _get_headers(self) -> Dict:
        """매 요청마다 랜덤 User-Agent 사용 (차단 우회 전략 #1)"""
        return {
            "User-Agent": random.choice(self.USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0",
            # Referer 추가 (더 자연스러운 요청처럼 보이게)
            "Referer": "https://www.10000recipe.com/",
        }
    
    def _polite_delay(self):
        """
        인간적인 요청 패턴 모방 (차단 우회 전략 #2)
        - 랜덤 딜레이 (2-5초)
        - 10번 요청마다 더 긴 휴식 (5-10초)
        """
        self._request_count += 1
        
        # 10번 요청마다 긴 휴식
        if self._request_count % 10 == 0:
            delay = random.uniform(5.0, 10.0)
            print(f"☕ [Polite] Taking a longer break... ({delay:.1f}s)")
        else:
            delay = random.uniform(2.0, 4.0)
        
        time.sleep(delay)
    
    def _safe_request(self, url: str, max_retries: int = 3) -> Optional[requests.Response]:
        """
        안전한 요청 (차단 우회 전략 #3)
        - 재시도 로직
        - 에러 핸들링
        - 403/429 응답 시 대기 후 재시도
        """
        for attempt in range(max_retries):
            try:
                self._polite_delay()
                response = self.session.get(url, headers=self._get_headers(), timeout=15)
                
                if response.status_code == 200:
                    return response
                elif response.status_code == 403:
                    print(f"⚠️ [Block] 403 Forbidden - Waiting longer... (attempt {attempt + 1})")
                    time.sleep(random.uniform(30, 60))  # 차단 시 30-60초 대기
                elif response.status_code == 429:
                    print(f"⚠️ [RateLimit] 429 Too Many Requests - Slowing down...")
                    time.sleep(random.uniform(60, 120))  # Rate limit 시 1-2분 대기
                else:
                    print(f"⚠️ Unexpected status: {response.status_code}")
                    
            except requests.exceptions.Timeout:
                print(f"⏳ Timeout on attempt {attempt + 1}")
            except requests.exceptions.RequestException as e:
                print(f"❌ Request error: {e}")
                
        return None

    def get_recipe_links(self, page: int = 1) -> List[str]:
        """
        레시피 목록 페이지에서 레시피 URL 추출
        """
        urls = []
        target_url = f"{self.BASE_URL}?order=reco&page={page}"
        print(f"📋 [List] Fetching page {page}...")
        
        response = self._safe_request(target_url)
        if not response:
            return urls
            
        try:
            soup = BeautifulSoup(response.text, 'lxml')
            seen = set()
            
            raw_links = soup.select('a[href^="/recipe/"]')
            for link in raw_links:
                href = link.get('href')
                if href and href.count('/') == 2 and href.split('/')[2].isdigit():
                    full_url = f"https://www.10000recipe.com{href}"
                    if full_url not in seen:
                        urls.append(full_url)
                        seen.add(full_url)
            
            print(f"✅ [List] Found {len(urls)} recipes on page {page}")
            
        except Exception as e:
            print(f"❌ Error parsing list: {e}")
            
        return urls

    def parse_recipe(self, url: str) -> Optional[Dict]:
        """
        레시피 상세 페이지 파싱
        """
        recipe_data = {"url": url, "name": None, "ingredients": [], "image": None}
        
        response = self._safe_request(url)
        if not response:
            return None
            
        try:
            soup = BeautifulSoup(response.text, 'lxml')
            
            # 1. Name
            title_elem = soup.select_one('div.view2_summary h3')
            if title_elem:
                recipe_data['name'] = title_elem.text.strip()
            else:
                return None  # 제목 없으면 스킵
                
            # 1.5 Steps (Instructions) - CRITICAL for Timeline Generation
            recipe_data['steps'] = []
            step_elems = soup.select('div.view_step div.view_step_cont')
            for step in step_elems:
                # Remove nested elements and get pure text
                step_text = step.text.strip().replace('\n', ' ')
                if step_text:
                    recipe_data['steps'].append(step_text)
            
            # 2. Ingredients
            ingre_items = soup.select('div.ready_ingre3 ul li')
            if not ingre_items:
                ingre_items = soup.select('#divConfirmedMaterialArea ul li')
            
            for item in ingre_items:
                qty_text = ""
                unit_span = item.select_one('span.ingre_unit')
                if unit_span:
                    qty_text = unit_span.text.strip()
                    unit_span.decompose()
                
                name_text = item.text.strip().replace('\n', '').replace('구매', '')
                
                if name_text:
                    recipe_data['ingredients'].append({"item": name_text, "qty": qty_text})
            
            # 재료가 없으면 스킵
            if not recipe_data['ingredients']:
                return None
            
            # 3. Image
            img_elem = soup.select_one('div.centeredcrop img') or soup.select_one('#main_photo img')
            if img_elem:
                recipe_data['image'] = img_elem.get('src')
                
            print(f"  ✅ {recipe_data['name']} ({len(recipe_data['ingredients'])} ingredients)")
            return recipe_data
                
        except Exception as e:
            print(f"❌ Error parsing recipe: {e}")
            return None

    def run_batch(self, count: int = 5, start_page: int = 1, seen_urls: set = None) -> tuple:
        """
        배치 크롤링 실행 (Deduplication supported)
        Returns: (List[Dict], int) -> (Results, NextPageToCrawl)
        """
        if seen_urls is None:
            seen_urls = set()

        print(f"🕷️ Starting batch crawl (Target: {count}, Seen: {len(seen_urls)})...")
        results = []
        page = start_page
        
        while len(results) < count:
            links = self.get_recipe_links(page=page)
            if not links:
                break
                
            for link in links:
                if len(results) >= count:
                    break
                
                # Deduplication Check
                if link in seen_urls:
                    # Optional: print only every 10th skip to reduce noise
                    # print(f"   ⏩ [Skip] Already collected: {link}")
                    continue

                try:
                    data = self.parse_recipe(link)
                    if data:
                        results.append(data)
                        seen_urls.add(link) # Update local set to prevent dups in same batch
                except Exception as e:
                     print(f"   ❌ Error processing {link}: {e}")
            
            page += 1
            if page > start_page + 100:  # Increased safety break for 100 items
                break

        print(f"🏁 Batch complete: {len(results)} recipes collected (Next Page: {page})")
        return results, page


if __name__ == "__main__":
    scraper = Recipe10kScraper()
    import json
    data = scraper.run_batch(count=5)
    print(json.dumps(data, indent=2, ensure_ascii=False))
