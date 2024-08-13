from PIL import Image, ImageDraw, ImageFont


def create_image(text, author, output_file):
    # 创建白色背景图片
    width, height = 800, 600
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)

    # 设置字体
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 60)
        text_font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 40)
        author_font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 30)
    except IOError:
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
        author_font = ImageFont.load_default()

    # 绘制标题
    draw.text((50, 50), "哲学", font=title_font, fill='green')

    # 绘制主要文本
    lines = text.split('\n')
    y_text = 150
    for line in lines:
        draw.text((50, y_text), line, font=text_font, fill='green')
        y_text += 50

    # 绘制英文翻译
    english_text = ["One particular weakness of human",
                    "nature is:",
                    "Care about what others think of you"]
    y_text += 50
    for line in english_text:
        draw.text((50, y_text), line, font=text_font, fill='green')
        y_text += 50

    # 绘制作者
    draw.text((width - 200, height - 50), f"— {author}", font=author_font, fill='green')

    # 保存图片
    image.save(output_file)


# 使用函数
text = "人性一个特别的弱点就是：\n在意别人如何看待自己"
author = "叔本华"
output_file = "philosophy_quote2.png"

create_image(text, author, output_file)
print(f"图片已保存为 {output_file}")