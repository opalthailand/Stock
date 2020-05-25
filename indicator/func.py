# เรียก library ที่จำเป็น
import datetime as dt 
import pandas as pd 
import pandas_datareader.data as web 
import numpy as np
import plotly
import plotly.offline as py
import plotly.graph_objs as go
from plotly.subplots import make_subplots

# มาจาก 1. General Function
## การดึงข้อมูลหุ้นให้อยู่ในรูป dataframe
def get_stock_data(stock_name,start_date,end_date = False):
    '''
    Input1: stock_name ชื่อหุ้น เช่น 'PTT', 'SCC', 'AOT'
    Input2: start_date วันเริ่มต้น โดยเขียนในรูปแบบ dt.date(2015,1,1) -> ปี เดือน วัน
    Input3: end_date วันสิ้นสุด หากมี ให้ใช้ format เหมือนกับ start_date โดยมีค่าเริ่มต้นไว้ที่ False ซึ่งหมายถึงว่า ให้เรียกผลวันสุดท้ายของข้อมูลที่มี
    Output: ตารางข้อมูล
    Description: ดึงข้อมูลหุ้นใดๆ ในตลาดหุ้น SET ตั้งแต่/ไปถึง วันเวลา ที่กำหนด
    '''
    stock_name =  f'{stock_name}.BK'
    if end_date == False:
        df = web.get_data_yahoo(stock_name, start_date)
    else:
        df = web.get_data_yahoo(stock_name, start_date, end_date)
    df.columns = df.columns.get_level_values(0)
    df.reset_index(inplace = True) 
    return df    

## การกำหนดสีของเส้นให้ต่างกัน
def color_list():
    '''
    Output: list ของชื่อสีที่แตกต่างกัน
    Description:  คืนค่าเป็น list ของชื่อสีที่แตกต่างกัน โดยการใช้งาน ทำได้โดย color_list()[0], color_list()[1], ...    
    '''
    return ['Blue','Orange','Purple','Gray','Pink','Gold','Violet']

## การเทียบเส้น indicator บนกราฟแท่งเทียนไปเลย
def get_candlestick(df,indicator=[]):
    '''
    Input1: df ตารางข้อมูลของหุ้นที่สนใจ
    Input2: indicator ชื่อของ column ที่ต้องการตีเส้นไปบนกราฟราคา โดยมีค่าเริ่มต้นไว้ที่ [] -> ไม่รับค่าใดๆ เมื่อต้องการใช้ ex ['EMA','SMA']
    Output: กราฟ candlestick 
    Description: นำตารางมาสร้างกราฟ candlestick และมีเส้น indicator กำกับจาก input2 ซึ่งแต่ละเส้น indicator จะมีสีจาก function ของการกำหนดสีของเส้นให้ต่างกัน
    '''
    # กราฟเดิมจากตัวอย่างก่อนหน้านี้
    fig = go.Figure(
            go.Candlestick(
                x=df['Date'],
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name="Price"))

    # ส่วนที่เพิ่มเข้ามาในการสร้าง indicator
    for i in range(len(indicator)):       
        fig.add_trace(
            go.Scatter(
                x=df["Date"],
                y=df[indicator[i]],
                name=indicator[i],
                line=dict(color=color_list()[i], width=1)))
    fig.show()

## การเทียบเส้น indicator กับกราฟแท่งเทียนตามแกนเวลา
def get_candlestick_subplot(df,indicator=[]):
    '''
    Input1: df ตารางข้อมูลของหุ้นที่สนใจ
    Input2: list ชื่อของ column/indicator ที่ต้องการตีเส้นไปบนกราฟใหม่เลย เช่น ['indicator1','indicator2']
    Output: กราฟ candlestick 
    Description: นำตารางมาสร้างกราฟ candlestick และกราฟ indicator แบบบนล่างตามแนวนอน ซึ่งแต่ละเส้น indicator จะมีสีจาก function ของการกำหนดสีของเส้นให้ต่างกัน
    '''
    # สร้าง layout ของกราฟ โดยกำหนดให้มี 2 rows กับ 1 column ใช้แกนเวลาร่วมกัน และทำให้กราฟสองกราฟติดกัน
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.02)

    # กราฟแท่งเทียนหลัก โดยกำหนดให้อยู่ row ล่างสุด
    fig.append_trace(
            go.Candlestick(
                x=df['Date'],
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name="Price"),
                2,1)

    # กราฟของ indicator โดยกำหนดให้อยู่ row บนกราฟแท่งเทียนหลัก
    for i in range(len(indicator)):       
        fig.add_trace(
            go.Scatter(
                x=df["Date"],
                y=df[indicator[i]],
                name=indicator[i],
                line=dict(color=color_list()[i], width=1)),
                1,1)

    fig.show()   
    
# มาจาก 2. Indicator: Simple Moving Average (SMA) and Exponential Moving Average (EMA)
# เขียนเป็น function ไว้สำหรับการเรียกใช้งานในอนาคต
def profit_from_cross(price_list,cross_list,buy='Golden',sell='Death'):
    '''
    Input1: price_list คือ list ของค่าที่บอกว่า ข้อมูลดังกล่าวมีราคาปิดเท่าไร
    Input2: cross_list คือ ของค่าที่บอกว่า ข้อมูลดังกล่าวเป็น golden/death cross
    Input3: string ที่บอกว่า ต้องมีคำไหนถึงจะบอกได้ว่า ข้อมูลนั้นควรซื้อ ซึ่งมี default = Golden
    Input4: string ที่บอกว่า ต้องมีคำไหนถึงจะบอกได้ว่า ข้อมูลนั้นควรขาย ซึ่งมี default = Death
    Output: ตัวเลขกำไร/ขาดทุน
    Description: คำนวนกำไร/ขาดทุนของ indicator ต่างๆ โดยจะมี formot ที่ให้เริ่ม golden cross จบด้วย death cross โดยที่ต้องเป็นข้อมูลที่ golden cross ลลับกับ death cross
    '''
    # แปลงให้ตัวแปรที่เข้ามาอยู่ในรูปของ list (ในกรณีที่ยังอยู๋ในรูปที่ยังมี index อยู่)
    price_list, cross_list = list(price_list), list(cross_list)
    # ทำให้ price_list ของเราเริ่มต้นด้วย Golden Cross แล้วจบด้วย Death Cross
    if buy not in cross_list[0]:
        price_list = price_list[1:]
    if sell not in cross_list[-1]:
        price_list = price_list[:-1]
    # คำนวนหาค่ากำไร/ขาดทุน
    golden_cross = price_list[0::2]
    death_cross = price_list[1::2]
    
    return sum(np.array(death_cross)-np.array(golden_cross))