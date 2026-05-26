import re
import time
import logging
import requests
from bs4 import BeautifulSoup
from config import HEADERS_TEMPLATE, PAGE_SIZE, MAX_RETRIES, BACKOFF_BASE, DELAY_LIST_PAGE, DELAY_DETAIL_PAGE, random_delay

logger = logging.getLogger(__name__)


def _make_session(cookie_str: str = "") -> requests.Session:
    session = requests.Session()
    session.headers.update(HEADERS_TEMPLATE)
    if cookie_str:
        session.headers["Cookie"] = cookie_str
    return session


def _request_with_retry(session: requests.Session, url: str) -> requests.Response | None:
    for attempt in range(MAX_RETRIES):
        try:
            resp = session.get(url, timeout=15)
            if resp.status_code == 200:
                if "sec.douban.com" in resp.url or "验证码" in resp.text:
                    logger.warning("触发验证码，停止抓取。请稍后重试。")
                    return None
                return resp
            if resp.status_code in (403, 429):
                wait = BACKOFF_BASE ** (attempt + 1)
                logger.warning(f"HTTP {resp.status_code}，等待 {wait}s 后重试 ({attempt+1}/{MAX_RETRIES})")
                time.sleep(wait)
                continue
            logger.error(f"HTTP {resp.status_code}: {url}")
            return None
        except requests.RequestException as e:
            wait = BACKOFF_BASE ** (attempt + 1)
            logger.warning(f"请求异常: {e}，等待 {wait}s 后重试 ({attempt+1}/{MAX_RETRIES})")
            time.sleep(wait)
    logger.error(f"重试 {MAX_RETRIES} 次后仍失败: {url}")
    return None


KNOWN_GENRES = {
    "剧情", "喜剧", "动作", "爱情", "科幻", "动画", "悬疑", "惊悚", "恐怖",
    "犯罪", "冒险", "奇幻", "战争", "历史", "传记", "音乐", "歌舞", "家庭",
    "纪录片", "西部", "武侠", "古装", "短片", "真人秀", "舞台艺术", "戏曲",
}
KNOWN_REGIONS = {
    "中国大陆", "中国香港", "中国台湾", "美国", "日本", "韩国", "英国", "法国",
    "德国", "意大利", "西班牙", "印度", "泰国", "澳大利亚", "加拿大", "俄罗斯",
    "墨西哥", "巴西", "瑞典", "丹麦", "荷兰", "波兰", "比利时", "奥地利",
    "爱尔兰", "新西兰", "新加坡", "马来西亚", "越南", "伊朗", "土耳其",
}
KNOWN_LANGUAGES = {
    "粤语", "汉语普通话", "英语", "日语", "韩语", "法语", "德语", "意大利语",
    "西班牙语", "俄语", "葡萄牙语", "泰语", "印地语", "阿拉伯语",
}


def _parse_intro(intro_text: str) -> dict:
    """
    解析列表页的 intro 字段，提取年份、导演、演员、地区、片长、类型等。
    格式示例: 1987-05-28(中国香港) / 吴宇森 / 周润发 / ... / 104分钟 / 剧情 / 犯罪
    """
    info = {}
    parts = [p.strip() for p in intro_text.split(" / ") if p.strip()]
    if not parts:
        return info

    # 第一段通常是日期和地区：1987-05-28(中国香港) 或 1987(中国香港) 或 1987
    first = parts[0]
    year_match = re.search(r"^(\d{4})", first)
    if year_match:
        info["year"] = year_match.group(1)

    region_match = re.search(r"\((.+?)\)", first)
    if region_match:
        info["region"] = region_match.group(1)

    remaining = parts[1:]  # 跳过第一段

    # 找到片长的位置，将字段分为"片长前"（人名）和"片长后"（类型/语言）
    duration_idx = -1
    for i, part in enumerate(remaining):
        if re.search(r"\d+\s*分钟", part):
            duration_idx = i
            info["duration"] = part
            break

    # 片长之前的字段：导演和演员（人名）
    # Douban 列表页格式：year(region) / 导演 / 演员1 / 演员2 / ... / 片长 / 类型 / 语言
    # 第一个人名通常是导演，后面是演员；无法可靠区分，只取第一个作为导演
    people = remaining[:duration_idx] if duration_idx >= 0 else remaining
    for part in people:
        part = part.strip()
        if not part:
            continue
        if part in KNOWN_REGIONS or part in KNOWN_LANGUAGES or part in KNOWN_GENRES:
            continue
        if not re.search(r"\d", part) and len(part) < 20:
            info["director"] = [part]  # 只取第一个人名作为导演
            break

    # 片长之后的字段：类型和语言
    if duration_idx >= 0:
        after_duration = remaining[duration_idx + 1:]
        genres = []
        languages = []
        for part in after_duration:
            part = part.strip()
            if part in KNOWN_GENRES:
                genres.append(part)
            elif part in KNOWN_LANGUAGES:
                languages.append(part)
        if genres:
            info["genre"] = genres
        if languages:
            info["language"] = languages

    return info


def _parse_list_page(html: str) -> list[dict]:
    """解析列表页，返回本页电影基本信息列表。"""
    soup = BeautifulSoup(html, "html.parser")
    items = soup.select(".grid-view .item")
    if not items:
        items = soup.select(".item")
    if not items:
        return []

    movies = []
    for item in items:
        movie = {}

        # 标题和详情链接
        title_tag = item.select_one(".title a")
        if title_tag:
            full_title = title_tag.get_text(strip=True)
            # 标题格式："中文名 / English Name"，取第一部分
            movie["title"] = full_title.split(" / ")[0].strip() if " / " in full_title else full_title
            movie["full_title"] = full_title
            href = title_tag.get("href", "")
            match = re.search(r"/subject/(\d+)/", href)
            if match:
                movie["subject_id"] = match.group(1)
                movie["url"] = href

        # 用户评分
        for tag in item.select("[class*='rating']"):
            for cls in tag.get("class", []):
                m = re.search(r"rating-star(\d)0", cls)
                if m:
                    movie["user_rating"] = int(m.group(1))
                    break

        # Intro 字段（包含年份、导演、演员、类型等）
        intro_tag = item.select_one(".intro")
        if intro_tag:
            intro_text = intro_tag.get_text(strip=True)
            parsed = _parse_intro(intro_text)
            movie.update(parsed)

        # 观影日期
        date_tag = item.select_one(".date")
        if date_tag:
            movie["watch_date"] = date_tag.get_text(strip=True)

        # 备注/短评
        comment_tag = item.select_one(".comment")
        if comment_tag:
            movie["comment"] = comment_tag.get_text(strip=True)

        # 标准化：将列表字段转为 " / " 分隔的字符串
        for key in ("director", "genre", "language", "cast", "region"):
            if key in movie and isinstance(movie[key], list):
                movie[key] = " / ".join(movie[key])

        if movie.get("title"):
            movies.append(movie)

    return movies


def _parse_detail_page(html: str) -> dict:
    """解析电影详情页，提取更精确的导演、类型、地区、年份、海报、简介。"""
    soup = BeautifulSoup(html, "html.parser")
    info = {}

    year_tag = soup.select_one("span.year")
    if year_tag:
        m = re.search(r"(\d{4})", year_tag.get_text())
        if m:
            info["year"] = m.group(1)

    # 海报图片
    mainpic = soup.select_one("#mainpic img")
    if mainpic and mainpic.get("src"):
        info["poster_url"] = mainpic["src"]

    # 剧情简介
    link_report = soup.select_one("#link-report span.all") or soup.select_one("#link-report span")
    if link_report:
        overview = link_report.get_text(strip=True)
        if overview:
            info["overview"] = overview

    info_div = soup.select_one("#info")
    if info_div:
        text = info_div.get_text()

        m = re.search(r"导演:\s*(.+?)(?:\n|主演|编剧|类型|制片|官方网站|语言|上映日期|片长|又名|IMDb)", text)
        if m:
            info["director"] = [d.strip() for d in re.split(r"\s*/\s*", m.group(1).strip()) if d.strip()]

        m = re.search(r"主演:\s*(.+?)(?:\n|编剧|类型|制片|官方网站|语言|上映日期|片长|又名|IMDb)", text)
        if m:
            info["cast"] = [c.strip() for c in re.split(r"\s*/\s*", m.group(1).strip()) if c.strip()]

        m = re.search(r"类型:\s*(.+?)(?:\n|制片|官方网站|语言|上映日期|片长|又名|IMDb)", text)
        if m:
            info["genre"] = [g.strip() for g in re.split(r"\s*/\s*", m.group(1).strip()) if g.strip()]

        m = re.search(r"制片国家/地区:\s*(.+?)(?:\n|语言|上映日期|片长|又名|IMDb|官方网站)", text)
        if m:
            info["region"] = [r.strip() for r in re.split(r"\s*/\s*", m.group(1).strip()) if r.strip()]

        m = re.search(r"语言:\s*(.+?)(?:\n|上映日期|片长|又名|IMDb|官方网站)", text)
        if m:
            info["language"] = [l.strip() for l in re.split(r"\s*/\s*", m.group(1).strip()) if l.strip()]

        m = re.search(r"片长:\s*(.+?)(?:\n|又名|IMDb|官方网站)", text)
        if m:
            info["duration"] = m.group(1).strip()

    return info


def scrape_all(user_id: str, cookie: str = "", detail: bool = False) -> list[dict]:
    """
    抓取用户所有标记为"看过"的电影。

    Args:
        user_id: 豆瓣用户 ID
        cookie: Cookie 字符串（可选）
        detail: 是否抓取详情页（默认关闭，列表页 intro 已包含足够信息）

    Returns:
        电影信息字典列表
    """
    session = _make_session(cookie)
    all_movies = []
    start = 0

    while True:
        url = f"https://movie.douban.com/people/{user_id}/collect?start={start}&sort=time&mode=grid&tags_all="
        logger.info(f"抓取列表页 start={start} ...")

        resp = _request_with_retry(session, url)
        if resp is None:
            logger.error("列表页请求失败，停止抓取。")
            break

        movies = _parse_list_page(resp.text)
        if not movies:
            logger.info("没有更多数据，抓取完成。")
            break

        logger.info(f"  本页获取 {len(movies)} 部电影")

        if detail:
            for i, movie in enumerate(movies):
                if "subject_id" not in movie:
                    continue
                detail_url = f"https://movie.douban.com/subject/{movie['subject_id']}/"
                logger.info(f"  抓取详情 [{i+1}/{len(movies)}]: {movie.get('title', '?')}")
                time.sleep(random_delay(DELAY_DETAIL_PAGE))
                detail_resp = _request_with_retry(session, detail_url)
                if detail_resp:
                    extra = _parse_detail_page(detail_resp.text)
                    # 详情页数据更精确，覆盖列表页解析结果
                    for k, v in extra.items():
                        if isinstance(v, list):
                            movie[k] = " / ".join(v)
                        else:
                            movie[k] = v

        all_movies.extend(movies)
        start += PAGE_SIZE
        time.sleep(random_delay(DELAY_LIST_PAGE))

    return all_movies
