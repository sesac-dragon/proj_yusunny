import streamlit as st
from streamlit_calendar import calendar
import pymysql
import pymysql.cursors
import pandas as pd
from DBconn import dbconn
from datetime import datetime, timedelta

def festival_calendar():
    now = datetime.now().date()
    thismonth = now.replace(day=1)
    nextmonth = thismonth.replace(month = thismonth.month+1)

    if 'start' not in st.session_state:
        st.session_state['start'] = thismonth
        st.session_state['end'] = nextmonth

    st.set_page_config("Festival Calendar", "💐", layout="wide")

    conn = pymysql.connect(**dbconn())

    print('MYSQL 연결 성공')

    start = st.session_state['start']
    end = st.session_state['end']

    with conn.cursor(cursor=pymysql.cursors.DictCursor) as cur:
        sql = """SELECT * 
            FROM tb_festival AS F
                JOIN tb_category AS C
                ON F.CategoryID = C.ID
                JOIN tb_area AS A
                ON F.AreaID = A.ID
                WHERE F.EndDate >= %s AND F.StartDate < %s;"""
        result = cur.execute(sql, (start, end))
        monthlyfstv = cur.fetchall()

    
    # st.header('🎊축제✨')
    st.markdown("""
    <h1 style='text-align: center; font-size: 40px;'>🎊가고 싶은 축제를 골라보자✨</h1>
    """, unsafe_allow_html=True)

    calendar_options = {
        "editable": False,
        "selectable": True,
        "headerToolbar": {
            "left": "today",
            "center": "title",
            "right": "prev,next"
        },
        "initialView": "dayGridMonth",
        "dayMaxEvents": 3,
        "locale": "kor",
        "height": "900px",
        "eventDisplay": "block",
    }

    custom_css="""
        .fc-event-past {
            opacity: 0.3;
        }

        .fc-event {
        border: 0px solid;
        border-radius: 6px;
        }

        .fc-event-title {
            font-weight: 700;
        }
        .fc-toolbar-title {
            font-size: 2rem;
        }
    """

    col2_1, col2_2 = st.columns([2, 1])

    with col2_1:
        df = pd.DataFrame(monthlyfstv)
        # st.dataframe(df)
        Catedf = df.groupby('CategoryName')
        Categorys = list(Catedf.groups.keys())

        Areadf = df.groupby('Area')
        Areas = list(Areadf.groups.keys())

        Categorys.insert(0, '전체 축제')
        Areas.insert(0, '전국')

        col1_1, col1_2 = st.columns(2)

        with col1_1:
            Area = st.selectbox('지역별', options=Areas)

        with col1_2:
            Category = st.selectbox('카테고리별', options=Categorys)

        color_list = [
            "#D9B44A",  # 진한 옅은 노랑
            "#D16F6F",  # 톤 다운된 레드
            "#7395FF",  # 부드러운 블루
            "#7AC88D",  # 톤 다운된 그린
            "#E6D98A",  # 따뜻한 옐로우
            "#9D85C5",  # 부드러운 퍼플
            "#74C7C7",  # 톤 다운 민트
            "#D78A9E",  # 부드러운 핑크
            "#7DB9FF",  # 은은한 하늘색
            "#DFAA69",  # 따뜻한 오렌지
        ]

        # n = random.choice(range(len(color_list)))
        calendar_events = []
        
        for i, fstv in enumerate(monthlyfstv):
            old = fstv['EndDate']
            enddate = old+timedelta(days=1)
            color = color_list[i % len(color_list)]
            f = {
                    "title": f"{fstv['Name']}",
                    "area": f"{fstv['AreaName']}",
                    "category": f"{fstv['CategoryName']}",
                    "start": f"{fstv['StartDate']}",
                    "end": f"{enddate}",
                    "dbId": f"{fstv['ID']}",
                    "color": color
                }
            if Area == '전국' and Category == '전체 축제':
                calendar_events.append(f)

            elif Area == '전국' and fstv['CategoryName'] == Category:
                calendar_events.append(f)

            elif Category == '전체 축제' and fstv['Area'] == Area :
                calendar_events.append(f)
            
            elif fstv['Area'] == Area and fstv['CategoryName'] == Category:
                calendar_events.append(f)
            
            # else:
            #     calendar_events = [{
            #         "title": '',
            #         "area": '',
            #         "category": '',
            #         "start": '',
            #         "end": '',
            #         "dbId": '',
            #         "color": color
            #     }]
            

        fcalendar = calendar(
            events=calendar_events,
            options=calendar_options,
            custom_css=custom_css,
            key='calendar',
            )



    # eventClick이 None 값일 때 = 축제 클릭 안하고 있을 때 에러 안나게 하기
    if fcalendar.get("eventClick") == None:
        selected_event = None

    # 선택한 축제 보여주기
    else:
        n = int(fcalendar["eventClick"]["event"]["extendedProps"]["dbId"])

        with conn.cursor(cursor=pymysql.cursors.DictCursor) as cur:
            result = cur.execute(
                f"""SELECT * 
                FROM tb_festival 
                WHERE ID = {n}""")
        selected_event = cur.fetchone()

    st.markdown("""
    <style>
    .oneline-title {
        display: block;
        font-weight: bold;
        white-space: nowrap;
        text-align: left;
        font-size: 2.2vw;  /* 뷰포트 너비 기준으로 폰트 크기 자동 조절 */
        letter-spacing: -0.03em;
        line-height: 1.2;
        margin: 1em 0;
    }
    </style>
    """, unsafe_allow_html=True)

    with col2_2:
        if 'before' not in st.session_state:
            st.session_state['before'] = selected_event

        if selected_event == None:
            st.session_state['before'] = None
            pass
        else:

            st.markdown(f"<div class='oneline-title'>🎆 {selected_event['Name']}</div>", unsafe_allow_html=True)
            st.write(f"📌 {selected_event['AreaName']}")
            st.markdown(f"![축제사진]({selected_event['ImageUrl']})")
            st.write(f"🗓 날짜: {selected_event['StartDate']} ~ {selected_event['EndDate']}")
            
            # st.session_state['more'] = False
            if st.session_state['before'] != selected_event:
                print('here')
                toggle_val2 = st.toggle("더보기", key="toggle2",value=False)
                toggle_val = toggle_val2
            else:
                toggle_val = st.toggle("더보기", key="toggle",value=False)
            
            if toggle_val == False:
                if len(selected_event['Contents'].strip()) <= 305:
                    st.write(f"📝: {selected_event['Contents']}")
                else:
                    st.write(f"📝: {selected_event['Contents'][:305]}...")
            else:                
                st.write(f"🚗 {selected_event['Address']}"+f" {selected_event['DetailAddress']}")
                
                if selected_event['HomepageUrl'] != '':
                    st.write(f"🏠 {selected_event['HomepageUrl']}")
                else: pass

                if selected_event['InstaUrl'] != '':
                    st.write(f"📱 {selected_event['InstaUrl']}")
                else: pass
            
                if selected_event['YoutubeUrl'] != '':
                    st.write(f"🎥 {selected_event['YoutubeUrl']}")
                else: pass

                if selected_event['Tel'] != '':
                    st.write(f"📞 {selected_event['Tel']}")
                else: pass
                
                st.write(f"📝 {selected_event['Contents']}")
            
            st.session_state['before'] = selected_event
            

    # 보여지는 월별로 화면 보이게 하기 위한 session_state
    if 'eventsSet' in fcalendar:
        st.session_state['start'] = fcalendar['eventsSet']['view']['activeStart'][:10]
        start = st.session_state['start']
        st.session_state['end'] = fcalendar['eventsSet']['view']['activeEnd'][:10]
        end = st.session_state['end']

    elif fcalendar.get("eventClick") == None:
        pass

    print(start, end)
    # print(calendar)
    
    
    st.subheader("축제 리스트", divider="rainbow", )
    with st.expander('목록'):
        showdf = pd.DataFrame(calendar_events).drop(columns=['dbId', 'color'])
        st.dataframe(showdf)
