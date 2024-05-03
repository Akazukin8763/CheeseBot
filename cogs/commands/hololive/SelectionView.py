import discord

import requests
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup

import numpy as np
import cv2

generations = {"Gen-0": [discord.SelectOption(label="Tokino Sora", description="ときのそら"),
                         discord.SelectOption(label="Robocosan", description="ロボ子さん"),
                         discord.SelectOption(label="AZKi", description="AZKi"),
                         discord.SelectOption(label="Sakura Miko", description="さくらみこ"),
                         discord.SelectOption(label="Hoshimachi Suisei", description="星街すいせい")],
               "Gen-1": [discord.SelectOption(label="Yozora Mel", description="夜空メル"),
                         discord.SelectOption(label="Aki Rosenthal", description="アキ・ローゼンタール"),
                         discord.SelectOption(label="Akai Haato", description="赤井はあと"),
                         discord.SelectOption(label="Shirakami Fubuki", description="白上フブキ"),
                         discord.SelectOption(label="Natsuiro Matsuri", description="夏色まつり")],
               "Gen-2": [discord.SelectOption(label="Minato Aqua", description="湊あくあ"),
                         discord.SelectOption(label="Murasaki Shion", description="紫咲シオン"),
                         discord.SelectOption(label="Nakiri Ayame", description="百鬼あやめ"),
                         discord.SelectOption(label="Yuzuki Choco", description="癒月ちょこ"),
                         discord.SelectOption(label="Oozora Subaru", description="大空スバル")],
               "Gamers": [discord.SelectOption(label="Shirakami Fubuki", description="白上フブキ"),
                          discord.SelectOption(label="Ookami Mio", description="大神ミオ"),
                          discord.SelectOption(label="Nekomata Okayu", description="猫又おかゆ"),
                          discord.SelectOption(label="Inugami Korone", description="戌神ころね")],
               "Gen-3": [discord.SelectOption(label="Usada Pekora", description="兎田ぺこら"),
                         discord.SelectOption(label="Shiranui Flare", description="不知火フレア"),
                         discord.SelectOption(label="Shirogane Noel", description="白銀ノエル"),
                         discord.SelectOption(label="Houshou Marine", description="宝鐘マリン")],
               "Gen-4": [discord.SelectOption(label="Amane Kanata", description="天音かなた"),
                         discord.SelectOption(label="Tsunomaki Watame", description="角巻わため"),
                         discord.SelectOption(label="Tokoyami Towa", description="常闇トワ"),
                         discord.SelectOption(label="Himemori Luna", description="姫森ルーナ"),
                         discord.SelectOption(label="Kiryu Coco", description="桐生ココ")],
               "Gen-5": [discord.SelectOption(label="Yukihana Lamy", description="雪花ラミィ"),
                         discord.SelectOption(label="Momosuzu Nene", description="桃鈴ねね"),
                         discord.SelectOption(label="Shishiro Botan", description="獅白ぼたん"),
                         discord.SelectOption(label="Omaru Polka", description="尾丸ポルカ")],
               "HoloX": [discord.SelectOption(label="La+ Darknesss", description="ラプラス・ダークネス"),
                         discord.SelectOption(label="Takane Lui", description="鷹嶺ルイ"),
                         discord.SelectOption(label="Hakui Koyori", description="博衣こより"),
                         discord.SelectOption(label="Sakamata Chloe", description="沙花叉クロヱ"),
                         discord.SelectOption(label="Kazama Iroha", description="風真いろは")],
               "Indonesia": [discord.SelectOption(label="Ayunda Risu", description="アユンダ・リス"),
                             discord.SelectOption(label="Moona Hoshinova", description="ムーナ・ホシノヴァ"),
                             discord.SelectOption(label="Airani Iofifteen", description="アイラニ・イオフィフティーン"),
                             discord.SelectOption(label="Kureiji Ollie", description="クレイジー・オリー"),
                             discord.SelectOption(label="Anya Melfissa", description="アーニャ・メルフィッサ"),
                             discord.SelectOption(label="Pavolia Reine", description="パヴォリア・レイネ"),
                             discord.SelectOption(label="Vestia Zeta", description="ベスティア・ゼータ"),
                             discord.SelectOption(label="Kaela Kovalskia", description="カエラ・コヴァルスキア"),
                             discord.SelectOption(label="Kobo Kanaeru", description="こぼ・かなえる")],
               "Myth": [discord.SelectOption(label="Mori Calliope", description="森カリオペ"),
                        discord.SelectOption(label="Takanashi Kiara", description="小鳥遊キアラ"),
                        discord.SelectOption(label="Ninomae Ina\'nis", description="一伊那尓栖/にのまえいなにす"),
                        discord.SelectOption(label="Gawr Gura", description="がうる・ぐら"),
                        discord.SelectOption(label="Watson Amelia", description="ワトソン・アメリア")],
               "Project: HOPE": [discord.SelectOption(label="IRyS", description="IRyS")],
               "Council": [discord.SelectOption(label="Tsukumo Sana", description="九十九佐命"),
                           discord.SelectOption(label="Ceres Fauna", description="セレス・ファウナ"),
                           discord.SelectOption(label="Ouro Kronii", description="オーロ・クロニー"),
                           discord.SelectOption(label="Nanashi Mumei", description="七詩ムメイ"),
                           discord.SelectOption(label="Hakos Baelz", description="ハコス・ベールズ")],
               "Office Staff": [discord.SelectOption(label="Friend-A", description="友人A（えーちゃん）"),
                                discord.SelectOption(label="Harusaki Nodoka", description="春先のどか")]}


def url_to_image(url):
    url = urllib.parse.quote(url, safe=':/')  # 避免爬蟲出來的路徑含有日文及漢字
    resp = urllib.request.urlopen(url)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    return image[:, :, ::-1]


def get_info(name: str):
    official_url = f"https://hololive.hololivepro.com/talents"

    # Official 頭像
    response = requests.get(official_url)
    soup = BeautifulSoup(response.text, "html.parser")

    _img = None
    _color = None
    _url = None
    for key, image in zip(soup.findAll("h3"), soup.findAll("img", class_="wp-post-image")):
        format_name = name.replace(' ', '').replace('\'', '')

        if format_name in key.getText().replace(' ', '').replace('\'', ''):
            _img = image.get("src")
            r, g, b = url_to_image(_img)[20, 20, :]
            _color = int(r * 65536 + g * 256 + b)
            _url = key.parent()[0].findParent().get("href")
            break

    # Official 詳細資料
    response = requests.get(_url)
    soup = BeautifulSoup(response.text, "html.parser")

    _description = soup.find("p", class_="catch").get_text() + '\n' + soup.find("p", class_="txt").get_text()
    _datas = soup.findAll("div", class_=["left", "right"])

    # Discord Embed
    embed = discord.Embed(title="Description", description=_description, color=_color)
    embed.set_author(name=name, icon_url=_img)
    embed.set_thumbnail(url=_img)

    embed.add_field(name=chr(173), value=chr(173), inline=False)

    for data in _datas:
        for dt, dd in zip(data.findAll("dt"), data.findAll("dd")):
            _field_name = dt.getText()
            _field_value = dd.getText()

            # 已建好表格，但尚未填寫資料
            if _field_value == "":
                continue

            embed.add_field(name=_field_name,
                            value=_field_value,
                            inline=True)

    return embed


class SelectGeneration(discord.ui.View):

    @discord.ui.select(placeholder="Select Generation", min_values=1, max_values=1,
                       options=[discord.SelectOption(label="Gen-0", description="0期生"),
                                discord.SelectOption(label="Gen-1", description="1期生"),
                                discord.SelectOption(label="Gen-2", description="2期生"),
                                discord.SelectOption(label="Gamers", description="ホロライブゲーマーズ"),
                                discord.SelectOption(label="Gen-3", description="3期生"),
                                discord.SelectOption(label="Gen-4", description="4期生"),
                                discord.SelectOption(label="Gen-5", description="5期生"),
                                discord.SelectOption(label="HoloX", description="秘密結社holoX"),
                                discord.SelectOption(label="Indonesia", description="ホロライブインドネシア"),
                                discord.SelectOption(label="Myth", description="Myth"),
                                discord.SelectOption(label="Project: HOPE", description="Project: HOPE"),
                                discord.SelectOption(label="Council", description="Council"),
                                discord.SelectOption(label="Office Staff", description="事務所スタッフ")])
    async def callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        _select = interaction.data['values'][0]

        # 建立子選項
        _talent = SelectTalent(f"Select {_select}")

        _talent.append_option(discord.SelectOption(label="<< Previous page"))
        for generation in generations[_select]:
            _talent.append_option(generation)

        await interaction.response.defer()
        await interaction.edit_original_message(view=discord.ui.View().add_item(_talent))


class SelectTalent(discord.ui.Select):

    def __init__(self, placeholder: str):
        super().__init__()
        self.placeholder = placeholder

    @discord.ui.select(min_values=1, max_values=1)
    async def callback(self, interaction: discord.Interaction):
        _select = interaction.data['values'][0]

        await interaction.response.defer()
        if _select == "<< Previous page":
            await interaction.edit_original_message(view=SelectGeneration())
        else:
            await interaction.edit_original_message(embed=get_info(_select))
