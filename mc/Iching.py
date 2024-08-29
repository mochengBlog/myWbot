import numpy as np
import time
import logging
import json

logger = logging.getLogger(__name__)

class IChing:
    def get_yao(self, seed=0):
        """生成一个爻"""
        np.random.seed(seed)
        start = 49  # 大衍之数五十，其用四十有九
        total = start
        logger.debug(f"开始生成爻，初始值: {total}")

        for _ in range(3):
            # 三次变易
            tian = np.random.randint(4, total - 4)  # 分二
            di = start - tian - 1  # 挂一
            tian_yushu = tian % 4 or 4  # 揲四归奇
            di_yushu = di % 4 or 4
            yushu = tian_yushu + di_yushu + (1 if _ == 0 else 0)
            total = total - yushu
            logger.debug(f"第 { _ + 1} 次变易后，剩余: {total}")

        result = total // 4
        logger.debug(f"生成的爻为: {result}")
        return result  # 6, 7, 8, 9 中的一个

    def get_hexagram(self):
        """生成本卦和变卦"""
        logger.info("开始生成本卦和变卦")
        ben_gua = [self.get_yao(seed=int(time.time()) + i) for i in range(6)]
        bian_gua, bian_gua_position = self.get_bian_gua(ben_gua)
        logger.info(f"生成的本卦: {ben_gua}")
        logger.info(f"生成的变卦: {bian_gua}")
        return ben_gua, bian_gua, bian_gua_position

    def get_bian_gua(self, num_list):
        """根据本卦生成变卦"""
        bian_gua = [7 if yao in [7, 6] else 8 for yao in num_list]
        bian_gua_position = [a != b for a, b in zip(num_list, bian_gua)]
        logger.debug(f"变卦生成: {bian_gua}")
        logger.debug(f"变爻位置: {bian_gua_position}")
        return bian_gua, bian_gua_position

    def get_guaming(self, num_list):
        """获取卦名的二进制表示"""
        yao_list = [str(yao % 2) for yao in reversed(num_list)]
        result = ''.join(yao_list)
        logger.debug(f"卦名二进制表示: {result}")
        return result

    @classmethod
    def giet_guaming_info(cls):
        iching = IChing()
        ben_gua, bian_gua, bian_gua_position = iching.get_hexagram()
        bengua_guaming = iching.get_guaming(ben_gua)
        biangua_guaming = iching.get_guaming(bian_gua)
        logger.info(f"本卦名: {bengua_guaming}")
        logger.info(f"变卦名: {biangua_guaming}")
        # 指定 JSON 文件的路径
        file_path = './IChingData.json'
        # 读取 JSON 文件
        with open(file_path, 'r', encoding='utf-8') as json_file:
            IChingData = json.load(json_file)
        # 从IChingData.json中获取 详情
        return IChingData[bengua_guaming], IChingData[biangua_guaming]

# 示例使用


if __name__ == "__main__":
    bengua , biangua = IChing.giet_guaming_info()
    print(bengua)
    print(biangua)
    # logging.basicConfig(level=logging.DEBUG)
    # iching = IChing()
    # ben_gua, bian_gua, bian_gua_position = iching.get_hexagram()
    # bengua_guaming = iching.get_guaming(ben_gua)
    # biangua_guaming = iching.get_guaming(bian_gua)
    # logger.info(f"本卦名: {bengua_guaming}")
    # logger.info(f"变卦名: {biangua_guaming}")
    # # 指定 JSON 文件的路径
    # file_path = './IChingData.json'
    # # 读取 JSON 文件
    # with open(file_path, 'r', encoding='utf-8') as json_file:
    #     IChingData = json.load(json_file)
    # #从IChingData.json中获取 详情
    # print(IChingData[bengua_guaming])
    # print(IChingData[biangua_guaming])
    # # 格式化并输出
    # formatted_output = f"变卦：{IChingData[biangua_guaming]['name']}\n卦辞：{IChingData[biangua_guaming]['text']}"
    # print(formatted_output)



