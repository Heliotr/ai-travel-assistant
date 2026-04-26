"""
数据库初始化工具模块
将备份数据库恢复到工作状态，并更新日期为当前日期
"""

import shutil
import sqlite3
import pandas as pd

# 目标数据库文件
local_file = "travel_new.sqlite"
# 备份数据库文件
backup_file = "travel2.sqlite"


def update_dates():
    """
    更新数据库中的日期，使其与当前时间对齐
    用于测试环境，确保数据库中的日期是相对较新的
    """
    # 使用备份文件覆盖现有文件（重置操作）
    shutil.copy(backup_file, local_file)

    conn = sqlite3.connect(local_file)

    # 获取所有表名
    tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn).name.tolist()
    tdf = {}

    # 读取每个表的数据
    for t in tables:
        tdf[t] = pd.read_sql(f"SELECT * from {t}", conn)

    # 计算时间差：使用flights表中最大日期作为参考
    example_time = pd.to_datetime(tdf["flights"]["actual_departure"].replace("\\N", pd.NaT)).max()
    current_time = pd.to_datetime("now").tz_localize(example_time.tz)
    time_diff = current_time - example_time

    # 更新bookings表中的日期
    tdf["bookings"]["book_date"] = (
            pd.to_datetime(tdf["bookings"]["book_date"].replace("\\N", pd.NaT), utc=True) + time_diff
    )

    # 更新航班表的日期列
    datetime_columns = ["scheduled_departure", "scheduled_arrival", "actual_departure", "actual_arrival"]
    for column in datetime_columns:
        tdf["flights"][column] = (
                pd.to_datetime(tdf["flights"][column].replace("\\N", pd.NaT)) + time_diff
        )

    # 将更新后的数据写回数据库
    for table_name, df in tdf.items():
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        del df
    del tdf

    conn.commit()
    conn.close()

    return local_file


if __name__ == '__main__':
    db = update_dates()
    print(f"数据库已更新: {db}")