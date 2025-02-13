from dataclasses import dataclass
from typing import List
from datetime import datetime, date, timedelta
import requests
import time


@dataclass
class Summaries:
    gained_xp: int = 0
    frozen: bool = False
    streak_extended: bool = False
    date: int = 0
    user_id: int = 0
    repaired: bool = False
    daily_goal_xp: int = 0
    num_sessions: int = 0
    total_session_time: int = 0


@dataclass
class DuolingoData:
    summaries: List[Summaries]


def check_duolingo_status(user_map):
    today = date.today()
    status_dict = {}

    for name, user_id in user_map.items():
        # 构建请求URL
        start_date_str = (date.today() - timedelta(days=7)).strftime("%Y-%m-%d")
        url = f"https://www.duolingo.cn/2017-06-30/users/{user_id}/xp_summaries"
        params = {
            "startDate": start_date_str,
            "_": int(time.time() * 1000)
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Referer": "https://www.duolingo.cn/"
        }

        try:
            # 发送请求获取数据
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()  # 检查HTTP错误
            data = response.json()
        except requests.exceptions.RequestException as e:
            status_dict[name] = {"status": "error", "message": f"请求失败: {str(e)}"}
            continue
        except ValueError as e:
            status_dict[name] = {"status": "error", "message": f"JSON解析失败: {str(e)}"}
            continue

        # 转换数据并排序
        def convert_keys(summary):
            key_mapping = {
                'gainedXp': 'gained_xp',
                'frozen': 'frozen',
                'streakExtended': 'streak_extended',
                'date': 'date',
                'userId': 'user_id',
                'repaired': 'repaired',
                'dailyGoalXp': 'daily_goal_xp',
                'numSessions': 'num_sessions',
                'totalSessionTime': 'total_session_time'
            }
            return {key_mapping.get(k, k): v for k, v in summary.items()}

        summaries_list = [Summaries(**convert_keys(summary)) for summary in data.get("summaries", [])]
        summaries_list.sort(key=lambda x: x.date)

        # 初始化打卡状态标志
        has_checked = False
        for summary in summaries_list:
            # 转换时间戳为日期
            local_date = datetime.fromtimestamp(summary.date).date()

            # 只检查当天的打卡状态
            if local_date == today:
                gained_xp = summary.gained_xp or 0
                status_dict[name] = {
                    "status": "已打卡" if gained_xp > 0 else "未打卡",
                    "gained_xp": gained_xp
                }
                has_checked = True
                break  # 找到当天记录后退出循环

        # 如果没有找到当天的记录，记录未打卡状态
        if not has_checked:
            status_dict[name] = {"status": "未打卡", "gained_xp": 0}

        time.sleep(0.1)

    return status_dict


def main():
    # 用户映射
    user_map = {
        "淘宝": 1411707690,
        "强哥（白国强）": 1475491603,
        "梦佬（梦短情长）": 1411686409,
        "大眼": 1405913981,
        "程佬（荣焱炎炎）": 1411679659,
        "杨峰": 30783396,
        "七喜": 1424644905,
        "远仔（懒得起名君）": 1430893956,
        "lo仔（loafer）": 1451803632
    }
    status_dict = check_duolingo_status(user_map)

    # 打印每个用户的打卡状态
    for name, status in status_dict.items():
        if status.get("status") == "error":
            print(f"{name}: {status['message']}")
        else:
            print(f"{name} {status['status']}")


if __name__ == "__main__":
    main()