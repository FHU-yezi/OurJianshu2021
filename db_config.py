from peewee import (BooleanField, CharField, DateTimeField, IntegerField,
                    Model, SqliteDatabase)


class RunLog(Model):
    id = IntegerField(primary_key=True)
    time = DateTimeField()
    level = IntegerField()
    message = CharField()

    class Meta:
        database = SqliteDatabase("log.db")


class ViewLog(Model):
    id = IntegerField(primary_key=True)
    time = DateTimeField()
    user_url = CharField(null=True)
    page_name = CharField(null=True)
    is_mobile = BooleanField()
    is_tablet = BooleanField()
    is_pc = BooleanField()
    browser_name = CharField()
    os_name = CharField()
    language = CharField()
    ip = CharField()

    class Meta:
        database = SqliteDatabase("log.db")


"""
用户状态码定义：
1：进入排队，未处理
2：处理中
3：处理完成，未查看
4：已查看
5：出错
"""


class User(Model):
    user_url = CharField(primary_key=True)
    user_name = CharField()
    status = IntegerField()
    add_time = DateTimeField()
    start_process_time = DateTimeField(null=True)
    finish_process_time = DateTimeField(null=True)
    first_show_summary_time = DateTimeField(null=True)
    exception_description = CharField(null=True)

    class Meta:
        database = SqliteDatabase("userdata.db")
        table_name = "user_queue"


def InitDB():
    RunLog.create_table()
    ViewLog.create_table()
    User.create_table()


InitDB()  # 导入模块时初始化数据库
