from pywebio import start_server
from pywebio.output import put_link, put_markdown
from pywebio.session import info as session_info

from config_manager import Config
from data_getter import init as data_getter_init
from log_manager import AddRunLog, AddViewLog
from message_sender import init as message_send_init
from status_monitor import init as status_monitor_init
from web_modules.join_queue import JoinQueue
from web_modules.letter_to_jianshuers import LetterToJianshuers
from web_modules.utils import GetLocalStorage, GetUrl, SetFooter
from web_modules.view_summary import ViewSummary

AddRunLog(3, f"版本号：{Config()['basic_data/version']}")


data_getter_init()
AddRunLog(3, "数据获取线程启动成功")

message_send_init()
AddRunLog(3, "消息发送线程启动成功")

status_monitor_init()
AddRunLog(3, "状态监控线程启动成功")


def index():
    """「风语」—— 简书 2021 年度总结
    """

    put_markdown("""
    # 「风语」—— 简书 2021 年度总结

    > 风起叶落，语存元夜。

    这是一名技术工作者呈现给社区的年度总结。
    """)
    AddViewLog(session_info, user_url=GetLocalStorage("user_url"), page_name="主页")

    put_markdown("""
    # 排队

    **为什么要排队？**

    生成年度总结所需的数据量较多，为避免给简书服务器造成压力，我们对请求频率进行了限制。

    同时，排队也可以帮助我们更好的分配服务器资源，让大家的年终总结生成效率得到提高。

    一般情况下，提交排队申请五分钟后即可查看年终总结。
    """)

    put_link("点击前往排队页面", url=f"{GetUrl()}?app=JoinQueue")

    put_markdown("""
    # 查看年终总结

    记得先排队哦~

    如果年终总结尚未生成，请稍等几分钟，可以趁着这段时间，看看下面的那封信。
    """)

    put_link("查看年终总结", url=f"{GetUrl()}?app=ViewSummary")

    put_markdown("""
    # 写给简友们的信

    这是「风语」的开发者写给大家的信，里面有开发这个项目的心路历程，和对简书生态的期望。
""")

    put_link("查看信件", url=f"{GetUrl()}?app=LetterToJianshuers")

    SetFooter(f"Version：{Config()['basic_data/version']} {Config()['basic_data/footer_content']}")


AddRunLog(3, "启动服务......")
start_server([JoinQueue, ViewSummary, LetterToJianshuers, index], port=Config()["service/port"])
