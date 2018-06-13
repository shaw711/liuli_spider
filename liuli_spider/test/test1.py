''' 2018年6月7日  2018-06-07'''
import datetime

def date_convert(value):
    try:
        create_date = datetime.datetime.strptime(value,"%Y%m%d").date()
    except Exception as e:
        create_date = datetime.datetime.now().date()
    return create_date
print(date_convert('2018年6月5日'))
print(datetime.datetime.strptime('2018年6月5日',"%Y年%m月%d日").date())
