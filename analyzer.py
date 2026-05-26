import os
import logging
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from config import CHINESE_FONTS, OUTPUT_DIR

logger = logging.getLogger(__name__)

# 中文字体配置
plt.rcParams["font.sans-serif"] = CHINESE_FONTS
plt.rcParams["axes.unicode_minus"] = False

# 风格
sns.set_theme(style="whitegrid", font=CHINESE_FONTS[0])


def _save(fig, name: str):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, name)
    fig.savefig(path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    logger.info(f"图表已保存: {path}")


def rating_distribution(df: pd.DataFrame):
    """用户评分分布柱状图"""
    if "user_rating" not in df.columns or df["user_rating"].isna().all():
        logger.warning("无评分数据，跳过评分分布图")
        return

    fig, ax = plt.subplots(figsize=(8, 5))
    rating_counts = df["user_rating"].dropna().astype(int).value_counts().sort_index()
    colors = sns.color_palette("YlOrRd", len(rating_counts))
    bars = ax.bar(rating_counts.index, rating_counts.values, color=colors, edgecolor="white")

    for bar, val in zip(bars, rating_counts.values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                str(val), ha="center", va="bottom", fontsize=11, fontweight="bold")

    ax.set_xlabel("评分（星）", fontsize=12)
    ax.set_ylabel("电影数量", fontsize=12)
    ax.set_title("我的豆瓣评分分布", fontsize=14, fontweight="bold")
    ax.set_xticks(range(1, 6))
    ax.set_xticklabels(["1星", "2星", "3星", "4星", "5星"])
    _save(fig, "rating_distribution.png")


def genre_preference(df: pd.DataFrame):
    """电影类型偏好饼图"""
    if "genre" not in df.columns or df["genre"].isna().all():
        logger.warning("无类型数据，跳过类型偏好图")
        return

    all_genres = []
    for g in df["genre"].dropna():
        if isinstance(g, list):
            all_genres.extend(g)
        elif isinstance(g, str):
            # 尝试解析字符串格式的列表
            if g.startswith("["):
                import ast
                try:
                    all_genres.extend(ast.literal_eval(g))
                except (ValueError, SyntaxError):
                    all_genres.extend([x.strip() for x in g.strip("[]").split(",")])
            else:
                all_genres.extend([x.strip() for x in g.split("/")])

    if not all_genres:
        logger.warning("类型数据为空，跳过")
        return

    genre_counts = pd.Series(all_genres).value_counts().head(10)

    fig, ax = plt.subplots(figsize=(9, 7))
    colors = sns.color_palette("Set3", len(genre_counts))
    wedges, texts, autotexts = ax.pie(
        genre_counts.values, labels=genre_counts.index, autopct="%1.1f%%",
        colors=colors, startangle=140, pctdistance=0.8,
        textprops={"fontsize": 11}
    )
    for t in autotexts:
        t.set_fontsize(10)
    ax.set_title("电影类型偏好 Top 10", fontsize=14, fontweight="bold")
    _save(fig, "genre_preference.png")


def watching_trend(df: pd.DataFrame):
    """观影趋势折线图（按月）"""
    if "watch_date" not in df.columns or df["watch_date"].isna().all():
        logger.warning("无观影日期数据，跳过观影趋势图")
        return

    dates = pd.to_datetime(df["watch_date"], errors="coerce", format="mixed")
    dates = dates.dropna()

    if dates.empty:
        logger.warning("日期解析后为空，跳过")
        return

    monthly = dates.dt.to_period("M").value_counts().sort_index()
    monthly.index = monthly.index.to_timestamp()

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(monthly.index, monthly.values, marker="o", markersize=4, linewidth=1.5,
            color="#E74C3C", markerfacecolor="#C0392B")
    ax.fill_between(monthly.index, monthly.values, alpha=0.15, color="#E74C3C")
    ax.set_xlabel("时间", fontsize=12)
    ax.set_ylabel("观影数量", fontsize=12)
    ax.set_title("观影趋势（按月）", fontsize=14, fontweight="bold")
    fig.autofmt_xdate()
    _save(fig, "watching_trend.png")


def rating_vs_year(df: pd.DataFrame):
    """评分 vs 电影年份散点图"""
    if "user_rating" not in df.columns or "year" not in df.columns:
        logger.warning("缺少评分或年份数据，跳过")
        return

    plot_df = df[["user_rating", "year"]].dropna()
    plot_df = plot_df.copy()
    plot_df["year"] = pd.to_numeric(plot_df["year"], errors="coerce")
    plot_df = plot_df.dropna()

    if plot_df.empty:
        logger.warning("评分-年份数据为空，跳过")
        return

    fig, ax = plt.subplots(figsize=(10, 6))
    # 添加抖动避免重叠
    import numpy as np
    jitter_y = plot_df["user_rating"] + np.random.normal(0, 0.1, len(plot_df))
    ax.scatter(plot_df["year"], jitter_y, alpha=0.5, s=30, c="#3498DB", edgecolors="white", linewidth=0.5)
    ax.set_xlabel("电影年份", fontsize=12)
    ax.set_ylabel("我的评分（星）", fontsize=12)
    ax.set_title("评分 vs 电影年份", fontsize=14, fontweight="bold")
    ax.set_yticks(range(1, 6))
    ax.set_yticklabels(["1星", "2星", "3星", "4星", "5星"])
    _save(fig, "rating_vs_year.png")


def top_directors(df: pd.DataFrame):
    """最爱导演 Top 15 水平柱状图"""
    if "director" not in df.columns or df["director"].isna().all():
        logger.warning("无导演数据，跳过导演偏好图")
        return

    all_directors = []
    for d in df["director"].dropna():
        if isinstance(d, list):
            all_directors.extend(d)
        elif isinstance(d, str):
            if d.startswith("["):
                import ast
                try:
                    all_directors.extend(ast.literal_eval(d))
                except (ValueError, SyntaxError):
                    all_directors.extend([x.strip() for x in d.strip("[]").split(",")])
            else:
                all_directors.extend([x.strip() for x in d.split("/")])

    if not all_directors:
        logger.warning("导演数据为空，跳过")
        return

    dir_counts = pd.Series(all_directors).value_counts().head(15)

    fig, ax = plt.subplots(figsize=(9, 7))
    colors = sns.color_palette("viridis", len(dir_counts))
    bars = ax.barh(dir_counts.index[::-1], dir_counts.values[::-1], color=colors, edgecolor="white")
    for bar, val in zip(bars, dir_counts.values[::-1]):
        ax.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height() / 2,
                str(val), ha="left", va="center", fontsize=11, fontweight="bold")
    ax.set_xlabel("电影数量", fontsize=12)
    ax.set_title("最爱导演 Top 15", fontsize=14, fontweight="bold")
    _save(fig, "top_directors.png")


def region_distribution(df: pd.DataFrame):
    """制片国家/地区分布柱状图"""
    if "region" not in df.columns or df["region"].isna().all():
        logger.warning("无地区数据，跳过地区分布图")
        return

    all_regions = []
    for r in df["region"].dropna():
        if isinstance(r, list):
            all_regions.extend(r)
        elif isinstance(r, str):
            if r.startswith("["):
                import ast
                try:
                    all_regions.extend(ast.literal_eval(r))
                except (ValueError, SyntaxError):
                    all_regions.extend([x.strip() for x in r.strip("[]").split(",")])
            else:
                all_regions.extend([x.strip() for x in r.split("/")])

    if not all_regions:
        logger.warning("地区数据为空，跳过")
        return

    region_counts = pd.Series(all_regions).value_counts().head(10)

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = sns.color_palette("coolwarm", len(region_counts))
    bars = ax.bar(region_counts.index, region_counts.values, color=colors, edgecolor="white")
    for bar, val in zip(bars, region_counts.values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                str(val), ha="center", va="bottom", fontsize=11, fontweight="bold")
    ax.set_xlabel("国家/地区", fontsize=12)
    ax.set_ylabel("电影数量", fontsize=12)
    ax.set_title("制片国家/地区分布 Top 10", fontsize=14, fontweight="bold")
    plt.xticks(rotation=30, ha="right")
    _save(fig, "region_distribution.png")


def monthly_pattern(df: pd.DataFrame):
    """观影月份模式柱状图"""
    if "watch_date" not in df.columns or df["watch_date"].isna().all():
        logger.warning("无观影日期数据，跳过月份模式图")
        return

    dates = pd.to_datetime(df["watch_date"], errors="coerce", format="mixed")
    dates = dates.dropna()

    if dates.empty:
        logger.warning("日期解析后为空，跳过")
        return

    month_names = ["1月", "2月", "3月", "4月", "5月", "6月",
                   "7月", "8月", "9月", "10月", "11月", "12月"]
    month_counts = dates.dt.month.value_counts().sort_index()
    # 确保 12 个月都有数据
    all_months = pd.Series(0, index=range(1, 13))
    all_months.update(month_counts)

    fig, ax = plt.subplots(figsize=(10, 5))
    colors = sns.color_palette("Spectral", 12)
    bars = ax.bar(month_names, all_months.values, color=colors, edgecolor="white")
    for bar, val in zip(bars, all_months.values):
        if val > 0:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.2,
                    str(int(val)), ha="center", va="bottom", fontsize=10, fontweight="bold")
    ax.set_xlabel("月份", fontsize=12)
    ax.set_ylabel("观影数量", fontsize=12)
    ax.set_title("观影月份分布", fontsize=14, fontweight="bold")
    _save(fig, "monthly_pattern.png")


def generate_all_charts(df: pd.DataFrame):
    """生成所有分析图表。"""
    logger.info("开始生成分析图表...")
    rating_distribution(df)
    genre_preference(df)
    watching_trend(df)
    rating_vs_year(df)
    top_directors(df)
    region_distribution(df)
    monthly_pattern(df)
    logger.info("所有图表生成完毕。")


def print_summary(df: pd.DataFrame):
    """打印统计摘要。"""
    print("\n" + "=" * 50)
    print("豆瓣观影数据统计摘要")
    print("=" * 50)
    print(f"总观影数量: {len(df)} 部")

    if "user_rating" in df.columns and df["user_rating"].notna().any():
        print(f"平均评分: {df['user_rating'].mean():.1f} 星")
        print(f"评分中位数: {df['user_rating'].median():.1f} 星")

    if "watch_date" in df.columns and df["watch_date"].notna().any():
        dates = pd.to_datetime(df["watch_date"], errors="coerce", format="mixed").dropna()
        if not dates.empty:
            print(f"观影时间跨度: {dates.min().strftime('%Y-%m-%d')} ~ {dates.max().strftime('%Y-%m-%d')}")

    if "year" in df.columns and df["year"].notna().any():
        years = pd.to_numeric(df["year"], errors="coerce").dropna()
        if not years.empty:
            print(f"电影年份跨度: {int(years.min())} ~ {int(years.max())}")

    if "director" in df.columns and df["director"].notna().any():
        all_directors = []
        for d in df["director"].dropna():
            if isinstance(d, list):
                all_directors.extend(d)
            elif isinstance(d, str):
                import ast
                try:
                    all_directors.extend(ast.literal_eval(d))
                except (ValueError, SyntaxError):
                    pass
        if all_directors:
            top = pd.Series(all_directors).value_counts().head(5)
            print(f"最爱导演: {', '.join([f'{d}({c}部)' for d, c in top.items()])}")

    print("=" * 50 + "\n")
