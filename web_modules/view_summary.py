from datetime import datetime
from typing import Dict

import plotly.express as px
from exceptions import UserDataDoesNotReadyException, UserDoesNotExistException
from JianshuResearchTools.assert_funcs import (AssertUserStatusNormal,
                                               AssertUserUrl)
from JianshuResearchTools.convert import UserUrlToUserSlug
from JianshuResearchTools.exceptions import InputError, ResourceError
from JianshuResearchTools.user import GetUserName
from log_service import AddRunLog
from pandas import DataFrame, read_csv
from PIL.Image import open as OpenImage
from pywebio.input import TEXT
from pywebio.output import (clear, put_button, put_buttons, put_html,
                            put_image, put_link, put_loading, put_table,
                            put_text, toast, use_scope)
from pywebio.pin import pin, put_input
from queue_manager import GetOneToShowSummary
from yaml import SafeLoader
from yaml import load as yaml_load

from .utils import GetLocalStorage, GetUrl, SetFooter, SetLocalStorage

with open("badge_to_type.yaml", "r", encoding="utf-8") as f:
    BADGE_TO_TYPE = yaml_load(f, SafeLoader)  # 初始化徽章类型表
    AddRunLog(4, "初始化徽章类型表成功")


def ShowSummary(basic_data: Dict, articles_data: DataFrame, wordcloud_path: str):
    AddRunLog(3, f"开始展示 {basic_data['url']}（{basic_data['name']}）的年度总结")
    with use_scope("output"):
        put_text("四季更替，星河流转，2021 是一个充满生机与挑战的年份。")
        put_text("简书，又陪伴你走过了一年。")
        put_image(basic_data["avatar_url"], width="100", height="100")  # 显示头像
        put_text(f"{basic_data['name']}，欢迎进入，你的简书 2021 年度总结。")
        put_text("（↓点击下方按钮继续↓）")
        put_text("\n")

    yield None

    with use_scope("output"):
        put_text(f"时至今日，你已经在简书写下了 {basic_data['articles_count']} 篇文章，"
                 f"一共 {round(basic_data['wordage'] / 10000, 1)} 万字。")
        if basic_data["wordage"] == 0:
            put_text("不妨去写写您的所思所想？")
        elif 0 < basic_data["wordage"] < 30000:
            put_text("继续加油创作哦，总会有人注意到你的光芒。")
        elif 30000 < basic_data["wordage"] < 100000:
            put_text("初出茅庐，你是否是未来的诸葛亮呢？")
        elif 100000 < basic_data["wordage"] < 300000:
            put_text("已经是一名勤于思考和创作的简友了，期待你成为顶流哦~")
        elif 300000 < basic_data["wordage"] < 1000000:
            put_text("创作你的创作，你把简书的 Slogan 践行到了极致。")
        elif basic_data["wordage"] >= 1000000:
            put_text("已经是社区中数一数二的存在了哦，让高质量的内容成为你的代名词吧。")
        put_text("\n")

        put_text(f"这些文字吸引了 {basic_data['fans_count']} 个粉丝，还有 {basic_data['likes_count']} 次点赞。")
        if basic_data["likes_count"] == 0:
            put_text("点赞？拿来吧你！")
        elif 0 < basic_data["likes_count"] < 100:
            put_text("无人问津？不，是未来无限！")
        elif 100 < basic_data["likes_count"] < 500:
            put_text("小有起色，爆发期即将到来！")
        elif 500 < basic_data["likes_count"] < 2000:
            put_text("已经有自己的忠实粉丝了哦，保持你的热情，继续加油！")
        elif 2000 < basic_data["likes_count"] < 5000:
            put_text("坚持写作，你会成为自己的忠实粉丝。")
        elif 5000 < basic_data["likes_count"] < 30000:
            put_text("天啊，这么高的关注度，你是靠内容还是互动得到的？")
        elif basic_data["likes_count"] > 30000:
            put_text("你写下的文字，为万千读者点亮了沿途的星光。")
        put_text("\n")

    yield None

    with use_scope("output"):
        put_text(f"你拥有 {basic_data['assets_count']} 资产，其中 {basic_data['FP_count']} 简书钻，{basic_data['FTN_count']} 简书贝。")
        if basic_data["assets_count"] < 5:
            put_text("难道你还不知道这都是些什么东西？去搜索一下吧！")
        elif 5 < basic_data["assets_count"] < 100:
            put_text("悄悄告诉你，写有深度的文章会提高收益哦！")
        elif 100 < basic_data["assets_count"] < 500:
            put_text("其实不必为资产发愁，毕竟简书是创作平台不是？")
        elif 500 < basic_data["assets_count"] < 1000:
            put_text("多与简友们互动会提高收益哦，简书会员也可以了解一下。")
        elif 1000 < basic_data["assets_count"] < 5000:
            put_text("这个资产量，不经常互动岂不是让收益白白溜走了？")
        elif 5000 < basic_data["assets_count"] < 30000:
            put_text("wow，好多钻贝啊，羡慕，资产管理经验分享一下可好？")
        elif 30000 < basic_data["assets_count"] < 100000:
            put_text("保持在社区的活跃、多写有深度的文章，是资产稳步增长的秘诀。")
        elif basic_data["assets_count"] > 100000:
            put_text("不管你是靠写文章还是使用钞能力，这个资产量绝对属于顶尖水准。")
        put_text("\n")

        put_text(f"你的钻贝比为 {basic_data['FP / FTN']}。")
        try:
            FP_percent = basic_data["FP_count"] / basic_data["assets_count"]
        except ZeroDivisionError:  # 没有资产导致除数为零
            FP_percent = 0
        if FP_percent == 0:
            put_text("你没有钻贝我怎么算？")
        elif 0 < FP_percent < 0.2:
            put_text("悄悄告诉你，贝转钻可以提高收益哦！")
        elif 0.2 < FP_percent < 0.4:
            put_text("贝这么多，一定是留着打赏自己喜欢的文章吧？")
        elif 0.4 < FP_percent < 0.6:
            put_text("钻贝均衡，不失为一种值得肯定的策略。")
        elif 0.6 < FP_percent < 0.8:
            put_text("靠简书钻提升权重，会员的加成卡也可以了解一下哦。")
        elif 0.8 < FP_percent <= 1:
            put_text("来点贝打赏给相中的文章怎么样？")
        put_text("\n")

    yield None
    with use_scope("output"):
        put_text(f"今年，你写下了 {articles_data['aslug'].count()} 篇文章，{round(articles_data['wordage'].sum() / 10000, 1)} 万字。")
        put_text(f"这一年，你写的文章，占总文章数的 {round(articles_data['aslug'].count() / basic_data['articles_count'], 2) * 100}%。")
        if articles_data["aslug"].count() < 5:
            put_text("期待在新的一年中看到你的更多文章！")
        elif 5 < articles_data["aslug"].count() < 30:
            put_text("书写更多内容，走向更广阔的天地吧！")
        elif 30 < articles_data["aslug"].count() < 100:
            put_text("笔耕不辍，你的努力值得被肯定！")
        elif 100 < articles_data["aslug"].count() < 300:
            put_text("你的文章很多，相信质量也很高吧！")
        elif articles_data["aslug"].count() > 300:
            put_text("每天在简书更新文章，已经成为了你的习惯！")
        put_text("\n")

        put_text(f"{articles_data['likes_count'].sum()} 个点赞，是你今年的成果，占你总收获的 {round(articles_data['likes_count'].sum() / basic_data['likes_count'] * 100, 2)}%。")
        if articles_data["likes_count"].sum() < 10:
            put_text("经常和简友互动，可以增加你在社区的影响力哦。")
        elif 10 < articles_data["likes_count"].sum() < 100:
            put_text("点赞，是简友们对你创作的认可，而这一切的基石，是你的文章质量。")
        elif 100 < articles_data["likes_count"].sum() < 500:
            put_text("很棒哦，你的文章质量很高，简友们都觉得你很棒！")
        elif 500 < articles_data["likes_count"].sum() < 2000:
            put_text("你已经会经常收到点赞了，让文章质量继续稳步提升吧！")
        elif 2000 < articles_data["likes_count"].sum() < 5000:
            put_text("你在社区已经有了自己的忠实读者，他们的支持，对你的影响力提升有不可磨灭的贡献。")
        elif articles_data["likes_count"].sum() > 5000:
            put_text("你得到了简友们的广泛认可，一呼百应用来形容你再适合不过了。")
        put_text("\n")

        put_text(f"你的最近一次创作在 {datetime.fromisoformat(list(articles_data[articles_data['is_top'] == False]['release_time'])[0]).replace(tzinfo=None).strftime(r'%Y 年 %m 月 %d 日')}，还记得当时写了什么吗？")
        put_text("\n")

    yield None

    with use_scope("output"):
        articles_data["month"] = articles_data["release_time"].apply(lambda x: datetime.fromisoformat(x).month)
        put_text(f"你哪个月发布的文章最多呢？答案是 {articles_data['month'].value_counts().index[0]} 月，"
                 f"这个月你发布了 {articles_data['month'].value_counts().values[0]} 篇文章。")

        with put_loading():
            graph_obj = px.line(articles_data.groupby("month").count(), y="title")
            graph_obj.update_layout(xaxis_title="月份", yaxis_title="发布文章数")
            put_html(graph_obj.to_html(include_plotlyjs="require", full_html=False))

    yield None

    with use_scope("output"):
        if basic_data['vip_type']:
            put_text(f"不知是什么原因，让你开通了{basic_data['vip_type']}会员呢？")
            put_text(f"你的会员在 {basic_data['vip_expire_time']} 到期，要不要考虑一下续费？")
        else:
            put_text("你貌似没有开通简书会员呢，全站去广告、发文数量上限提升等等特权，了解一下？")
        put_text("\n")
    yield None
    with use_scope("output"):
        if basic_data['badges_list']:
            put_text(f"你拥有 {len(basic_data['badges_list'])} 枚徽章：")
            put_table([[x, BADGE_TO_TYPE.get(x, "未知")] for x in basic_data["badges_list"]], ["徽章名称", "分类"])
        else:
            put_text("什么？你还没有徽章？为何不多写点文章申请个创作者，或者去做岛主？")
            put_text("搞点东西装饰一下你的个人主页，何乐而不为呢？")
        put_text("\n")
    yield None
    with use_scope("output"):
        put_text(f"知道 {basic_data['next_anniversary_day'].strftime(r'%Y 年 %m 月 %d 日')}是什么日子吗？")
        put_text("是你来简书的周年纪念日哦！到时候要不要发篇文章说说自己的感想？")
        put_text("\n")
    yield None
    with use_scope("output"):
        put_text("你的年度热词是什么呢？看看这张词云图吧：")
        with put_loading():
            put_image(OpenImage(wordcloud_path), format="png")
        put_text("\n")

    yield None
    with use_scope("output"):
        put_text(f"在大家面前，你的名字是{basic_data['name']}，而在简书的数据库中，你的代号是 {basic_data['id']}。")
        put_text("技术，无限可能，正如你面前的这份年终总结一样。")
        put_text("虽然它在背后，但你的每一份创作体验，都少不了万千技术工作者的默默付出。")
        put_text("\n")
    yield None
    with use_scope("output"):
        put_text("这是，属于你的创作总结；")
        put_text("这是，属于你的一年；")
        put_text("这是，属于你的简书社区。")
        put_text("\n")
    yield None

    with use_scope("output"):
        put_text("愿每一行文字，都能被知晓；")
        put_text("愿每一名创作者，都能找到自己的价值；")
        put_text("愿每一份不甘，都有温暖相伴。")
        put_text("\n")
    yield None
    with use_scope("output"):
        put_text("我们是简友，我们在简书等你。")
        put_text("\n")
    yield None
    with use_scope("output"):
        put_text("年终总结，完。")
        put_text("2022，启航！")

    clear("continue_button_area")  # 移除继续按钮
    exit()


def GetAllData() -> None:
    user_url = pin["user_url"]  # 从输入框中获取 user_url
    if not user_url:  # 输入框为空
        return

    try:
        AddRunLog(4, f"开始对 {user_url} 进行校验")
        AssertUserUrl(user_url)
        AssertUserStatusNormal(user_url)
    except (InputError, ResourceError):
        toast("输入的链接无效，请检查", color="warn")
        AddRunLog(4, f"{user_url} 无效")
        return
    else:
        user_name = GetUserName(user_url, disable_check=True)
        AddRunLog(4, f"{user_url} 校验成功，对应的用户名为 {user_name}")

    try:
        user_url = GetOneToShowSummary(user_url).user_url  # 将数据库中的用户状态更改为已查看年度总结
    except UserDoesNotExistException:
        toast("您未加入队列，请先排队", color="warn")
        with use_scope("data_input", clear=True):
            put_input("user_url", type=TEXT, label="您的简书用户主页链接")
            put_button("提交", color="success", onclick=GetAllData, disabled=True)  # 禁用提交按钮
        put_link("点击前往排队页面", url=f"{GetUrl().replace('?app=ViewSummary', '')}?app=JoinQueue")
        AddRunLog(4, f"{user_url}（{user_name}）未排队")
        return
    except UserDataDoesNotReadyException:
        toast("您的数据还未获取完成，请稍后再试", color="warn")
        with use_scope("data_input", clear=True):
            put_input("user_url", type=TEXT, value=user_url, label="您的简书用户主页链接")
            put_button("提交", color="success", onclick=GetAllData)
            put_text(f"尊敬的简友 {user_name}，我们正在努力获取您的数据，请稍后再试。")
        AddRunLog(4, f"{user_url}（{user_name}）的数据未就绪")
        return
    else:
        AddRunLog(4, f"{user_url}（{user_name}）的数据已就绪")
        user_slug = UserUrlToUserSlug(user_url)
        with open(f"user_data/{user_slug}/basic_data_{user_slug}.yaml", "r", encoding="utf-8") as f:
            basic_data = yaml_load(f, SafeLoader)
        AddRunLog(4, f"成功加载 {user_url}（{user_name}）的基础数据")
        with open(f"user_data/{user_slug}/article_data_{user_slug}.csv", "r", encoding="utf-8") as f:
            article_data = read_csv(f)
        AddRunLog(4, f"成功加载 {user_url}（{user_name}）的文章数据")
        clear("data_input")  # 清空数据输入区
        SetLocalStorage("user_url", user_url)  # 将用户链接保存到本地
        with use_scope("output"):  # 初始化输出区
            pass
        show_summary_obj = ShowSummary(basic_data, article_data, f"user_data/{user_slug}/wordcloud_{user_slug}.png")
        with use_scope("continue_button_area"):
            put_buttons([dict(label="继续", value="continue", color="dark")],
                        outline=True, onclick=lambda _: next(show_summary_obj), serial_mode=True)


def ViewSummary():
    """我的简书 2021 年终总结 ——「风语」
    """
    user_url = GetLocalStorage("user_url")
    AddRunLog(4, f"获取到用户本地存储的数据为：{user_url}")
    with use_scope("data_input", clear=True):
        put_input("user_url", type=TEXT, value=user_url, label="您的简书用户主页链接")
        put_button("提交", color="success", onclick=GetAllData)

    SetFooter("Made with PyWebIO and ♥")
