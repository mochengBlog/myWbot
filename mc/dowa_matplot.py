from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

class ChatStats:
    def __init__(self, start_time, end_time):
        self.start_time = start_time
        self.end_time = end_time
        self.speakers = 20
        self.messages = 52
        self.top_speakers = {
            "909": 11,
            "莫娜": 9,
            "消失的鱼": 4,
            "浩海路佩奇": 4,
            "调试调戏机器人,都暻": 3
        }
        self.messages_per_hour = 5
        self.peak_hour = "15:00-16:00"
        self.peak_messages = 19
        self.other_top = {"消失的鱼": 2}

    def generate_image(self, filename="chat_stats.png"):
        # 创建图像
        width, height = 400, 600
        image = Image.new('RGB', (width, height), color='#2b2b2b')
        draw = ImageDraw.Draw(image)

        # 使用默认字体
        title_font = ImageFont.load_default()
        normal_font = ImageFont.load_default()

        # 绘制标题
        draw.text((20, 20), "群聊数据统计", font=title_font, fill='#ffffff')

        # 绘制时间段
        y = 70
        draw.text((20, y), "Time Period", font=normal_font, fill='#ffffff')
        y += 20
        draw.text((20, y), f"• Start: {self.start_time}", font=normal_font, fill='#ffffff')
        y += 20
        draw.text((20, y), f"• End: {self.end_time}", font=normal_font, fill='#ffffff')

        # 绘制发言统计
        y += 30
        draw.text((20, y), "Messages", font=normal_font, fill='#ffffff')
        y += 20
        draw.text((20, y), f"• Speakers: {self.speakers}", font=normal_font, fill='#ffffff')
        y += 20
        draw.text((20, y), f"• Total messages: {self.messages}", font=normal_font, fill='#ffffff')

        # 绘制发言TOP5
        y += 30
        draw.text((20, y), "Top 5 Speakers", font=normal_font, fill='#ffffff')
        y += 20
        for i, (speaker, count) in enumerate(sorted(self.top_speakers.items(), key=lambda x: x[1], reverse=True)[:5], 1):
            draw.text((20, y), f"{i}. [{speaker}] : {count}", font=normal_font, fill='#ffffff')
            y += 20

        # 绘制消息频率
        y += 20
        draw.text((20, y), "Message Frequency", font=normal_font, fill='#ffffff')
        y += 20
        draw.text((20, y), f"• Per hour: {self.messages_per_hour}", font=normal_font, fill='#ffffff')
        y += 20
        draw.text((20, y), f"• Peak: {self.peak_hour} ({self.peak_messages})", font=normal_font, fill='#ffffff')

        # 绘制其他TOP名单
        y += 30
        draw.text((20, y), "Other Top Lists", font=normal_font, fill='#ffffff')
        y += 20
        for category, count in self.other_top.items():
            draw.text((20, y), f"• [{category}] Images: {count}", font=normal_font, fill='#ffffff')
            y += 20

        # 保存图像
        image.save(filename)
        print(f"Image saved as {filename}")

# 使用示例
stats = ChatStats("2024-08-15 00:00:00", "2024-08-15 23:59:59")
stats.generate_image()