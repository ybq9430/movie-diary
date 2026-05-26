import os
import sys
import argparse
import logging
import pandas as pd

from config import OUTPUT_DIR
from scraper import scrape_all
from analyzer import generate_all_charts, print_summary

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="豆瓣电影观影记录抓取与分析")
    parser.add_argument("--user-id", default="183593062", help="豆瓣用户 ID")
    parser.add_argument("--cookie", default="", help="浏览器 Cookie 字符串（可选，公开主页不需要）")
    parser.add_argument("--detail", action="store_true", default=True,
                        help="抓取详情页获取导演/类型/地区等信息（默认开启）")
    parser.add_argument("--no-detail", dest="detail", action="store_false",
                        help="跳过详情页抓取，仅获取列表页基础信息")
    parser.add_argument("--no-charts", action="store_true", help="跳过图表生成")
    parser.add_argument("--csv", default=None, help="指定 CSV 输出路径")
    args = parser.parse_args()

    csv_path = args.csv or os.path.join(OUTPUT_DIR, "douban_movies.csv")

    # 1. 抓取
    logger.info(f"开始抓取用户 {args.user_id} 的观影记录...")
    movies = scrape_all(args.user_id, args.cookie, detail=args.detail)

    if not movies:
        logger.error("未抓取到任何数据，请检查用户 ID 和 Cookie 是否正确。")
        sys.exit(1)

    logger.info(f"共抓取 {len(movies)} 部电影")

    # 2. 保存 CSV
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df = pd.DataFrame(movies)
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    logger.info(f"数据已保存到: {csv_path}")

    # 3. 生成图表
    if not args.no_charts:
        generate_all_charts(df)

    # 4. 打印摘要
    print_summary(df)


if __name__ == "__main__":
    main()
