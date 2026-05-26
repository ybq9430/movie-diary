import json
import httpx
from config import MIMO_BASE_URL, MIMO_API_KEY, MIMO_MODEL

_client = httpx.AsyncClient(timeout=120)


async def close():
    await _client.aclose()


async def generate_text(system_prompt: str, user_message: str, max_tokens: int = 4096) -> str:
    resp = await _client.post(
        f"{MIMO_BASE_URL}/v1/messages",
        headers={
            "x-api-key": MIMO_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": MIMO_MODEL,
            "max_tokens": max_tokens,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_message}],
        },
    )
    resp.raise_for_status()
    data = resp.json()
    content = data.get("content", [])
    if content and isinstance(content, list):
        return content[0].get("text", "")
    return ""


async def generate_personality(movies_data: list[dict]) -> str:
    system_prompt = """你是一位专业的电影心理学分析师。根据用户的观影历史，分析其观影性格和人格特征。
请从以下维度进行分析：
1. 观影人格类型（用一个有趣的类型名称）
2. 类型偏好分析（喜欢什么类型，为什么）
3. 导演品味画像（偏好什么风格的导演）
4. 观影习惯分析（观影频率、时间分布等）
5. 情感倾向（偏好什么情感基调的电影）
6. 人格洞察（从观影习惯推断的性格特征）
7. 推荐方向（未来可能喜欢的电影方向）

请用有趣、温暖的语气撰写，适当使用比喻和引用。输出格式为 Markdown。"""

    # Build movie summary
    total = len(movies_data)
    genres = {}
    directors = {}
    ratings = []
    regions = {}
    for m in movies_data:
        for g in (m.get("genres") or []):
            genres[g] = genres.get(g, 0) + 1
        for d in (m.get("directors") or []):
            directors[d] = directors.get(d, 0) + 1
        if m.get("user_rating"):
            ratings.append(m["user_rating"])
        for r in (m.get("regions") or []):
            regions[r] = regions.get(r, 0) + 1

    top_genres = sorted(genres.items(), key=lambda x: -x[1])[:10]
    top_directors = sorted(directors.items(), key=lambda x: -x[1])[:10]
    top_regions = sorted(regions.items(), key=lambda x: -x[1])[:5]
    avg_rating = sum(ratings) / len(ratings) if ratings else 0

    user_message = f"""以下是该用户的观影数据摘要：

总观影数量：{total} 部
平均评分：{avg_rating:.1f} 星（5星制）

最喜欢的类型（前10）：
{chr(10).join(f"- {g}: {c}部" for g, c in top_genres)}

最喜欢的导演（前10）：
{chr(10).join(f"- {d}: {c}部" for d, c in top_directors)}

最常看的地区（前5）：
{chr(10).join(f"- {r}: {c}部" for r, c in top_regions)}

请基于以上数据进行深度分析。"""

    return await generate_text(system_prompt, user_message)


async def generate_portrait_prompt(movies_data: list[dict], style: str) -> str:
    system_prompt = """你是一位AI艺术提示词专家。根据用户的观影品味，生成一段用于AI绘画的英文提示词（prompt），
描述一幅代表该用户观影性格的肖像画。

要求：
1. 提示词为英文
2. 包含艺术风格、色彩、构图、人物特征等细节
3. 融入用户最喜欢的电影类型元素
4. 长度控制在100-200词"""

    genres = {}
    for m in movies_data:
        for g in (m.get("genres") or []):
            genres[g] = genres.get(g, 0) + 1
    top_genres = sorted(genres.items(), key=lambda x: -x[1])[:5]
    genre_str = ", ".join(f"{g}({c}部)" for g, c in top_genres)

    user_message = f"""用户最喜欢的电影类型：{genre_str}
用户共看过 {len(movies_data)} 部电影
期望的画风：{style}

请生成一幅代表该用户观影性格的AI肖像画提示词。"""

    return await generate_text(system_prompt, user_message, max_tokens=500)


async def generate_recommendations(movies_data: list[dict], count: int = 10) -> list[dict]:
    system_prompt = """你是一位资深电影推荐专家。根据用户的观影历史，推荐用户可能喜欢但还没看过的电影。

要求：
1. 推荐的电影不能在用户已看过的列表中
2. 每部电影给出中文片名和推荐理由
3. 推荐理由要结合用户的观影偏好
4. 尽量推荐不同类型、不同地区的优质电影
5. 输出JSON数组格式，每个元素包含 title 和 reason 字段"""

    watched_titles = [m.get("title", "") for m in movies_data[:200]]
    genres = {}
    for m in movies_data:
        for g in (m.get("genres") or []):
            genres[g] = genres.get(g, 0) + 1
    top_genres = sorted(genres.items(), key=lambda x: -x[1])[:8]

    user_message = f"""用户最喜欢的电影类型：{', '.join(f'{g}({c}部)' for g, c in top_genres)}
用户已看过的部分电影（不要推荐这些）：
{', '.join(watched_titles[:100])}

请推荐 {count} 部电影。只输出JSON数组，不要其他内容。格式：
[{{"title": "电影名", "reason": "推荐理由"}}]"""

    result = await generate_text(system_prompt, user_message, max_tokens=2000)
    # Try to parse JSON from the response
    try:
        # Find JSON array in the response
        start = result.find("[")
        end = result.rfind("]") + 1
        if start >= 0 and end > start:
            return json.loads(result[start:end])
    except (json.JSONDecodeError, ValueError):
        pass
    return []
