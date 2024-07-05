from enum import Enum
import re


class Category(Enum):
    BEAUTY = 1
    EMOTION = 2
    SCENERY = 3
    ANIME = 4
    CITY = 5
    VISUAL = 6
    CREATIVE = 7
    TALE = 8
    MECH = 9
    GAME = 10
    ANIMAL = 11
    ART = 12
    TEXT = 13
    CELEBRITY = 14
    MAN = 15
    JAPANESE = 16


# 定义一个字典来映射输入字符串到枚举成员
category_mapping = {
    '美女': Category.BEAUTY,
    '情感': Category.EMOTION,
    '风景': Category.SCENERY,
    '动漫': Category.ANIME,
    '城市': Category.CITY,
    '视觉': Category.VISUAL,
    '创意': Category.CREATIVE,
    '物语': Category.TALE,
    '机械': Category.MECH,
    '游戏': Category.GAME,
    '动物': Category.ANIMAL,
    '艺术': Category.ART,
    '文字': Category.TEXT,
    '明星': Category.CELEBRITY,
    '男人': Category.MAN,
    '日系': Category.JAPANESE,
}


def get_category_value(input_str):
    # 根据输入的字符串获取枚举值
    input_str = input_str.strip()  # 去除可能的前后空白字符
    category = category_mapping.get(input_str)
    if category is not None:
        return category.value
    else:
        return "Enum value not found for the given input."


def get_category_name(value: str) -> str:
    # 根据枚举值获取枚举名称
    for name, enum_value in category_mapping.items():
        if name in value:
            return get_category_value(name)
    return "1"


if __name__ == '__main__':
    print(get_category_name('城市sd '))
    # print(get_category_name('美女111'))
