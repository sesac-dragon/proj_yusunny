from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
import os
import pymysql
import pymysql.cursors
from DBconn import dbconn
from dotenv import load_dotenv
import time

def category_analysis():
    
    load_dotenv()

    os.environ["OPENAI_API_KEY"]

    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

    prompt_template = PromptTemplate(
        input_variables=["festival_name", "festival_description"],
        template="""
        너는 축제를 카테고리로 분류하는 분류기야.

        아래 축제의 이름과 설명을 참고하여, 다음 중 하나로 분류해줘:
        1. 음식 축제: 축제의 핵심 주제나 주요 프로그램이 음식, 시식, 먹거리 체험 중심일 때 해당합니다. 단순히 설명에 음식이 언급되었다고 해서 무조건 음식 축제는 아니며, 음식이 메인이 아닐 경우 다른 카테고리로 분류합니다.
        2. 역사/전통/문화재 축제: 역사적 인물, 사건, 문화유산, 전통 의식, 전통놀이, 민속문화, 유교·불교 등 종교문화가 축제의 핵심 주제인 경우. 유네스코 세계유산이나 문화재에서 열리거나, 이를 소재로 한 공연·전시·체험 프로그램 포함.
        3. 문화/공연/전시 축제: 축제의 주된 목적이 공연, 강연, 전시, 책, 영화 등 문화 콘텐츠 자체일 때. 문화 콘텐츠가 중심이며, 지역 홍보나 상권 활성화가 주된 목적이 아닐 경우 해당.
        4. 자연/식물(꽃·정원·산·숲) 축제: 꽃, 단풍, 숲길, 식물원, 수목원 등 ‘자연 대상’ 감상이 주된 목적일 때 포함. 단, ‘계절’(봄·여름·가을·겨울) 테마 중심이 아닌 경우만 해당.
        5. 계절 테마 축제: 축제의 핵심 콘텐츠가 특정 계절의 분위기, 체험, 놀이, 이벤트 등 ‘계절 경험’일 때만 해당. 축제 기간이나 계절 단어만 포함되어서는 분류하지 않으며, 지역 홍보, 상권 활성화, 문화 콘텐츠가 주된 목적일 경우 계절 축제로 분류하지 않음. ‘봄’, ‘여름’ 등 계절 단어만 단순 등장하는 경우도 제외.
        6. 지역 축제: 축제의 주요 목적이 특정 지역의 고유 특성 홍보, 지역 경제 활성화, 관광 유치, 지역 브랜드 또는 특산물 홍보일 때. 문화·공연 프로그램이 있어도 ‘지역 알리기’와 ‘상권 활성화’가 중심이면 이 카테고리로 분류.
        7. 기타: 위 기준 어디에도 명확히 포함되지 않는 경우 (예: 반려동물 박람회, 체험 캠프 등).


        출력은 반드시 카테고리 번호인 숫자 형식으로 줘.

        밑에 예시를 참고해서 꼭 숫자형으로 출력해줘!



        1. 예시 입력:
        축제 이름: 공주 페스티벌
        설명: '공주 페스티벌'은 공주시에서 펼쳐지는 공주(Princess) 컨셉의 야간관광 콘텐츠이다. 제민천 감영길 일대에서 펼쳐지는 공주(Princess)컨셉의 야간 퍼레이드, 야간 플리마켓, 공주들의 이벤트는 계절별 다른 컨셉으로 제민천을 찾아온다. 봄, 여름, 가을, 겨울 사계절을 주제로 펼쳐질 공주들의 페스티벌은 제민천 감영길 일대를 색다르게 물들일 예정이다.

        1. 예시 출력: 
        6

        2. 예시 입력:
        축제 이름: 정남진 장흥 물축제
        설명: 정남진 장흥 물축제는 2025 문화체육관광부 문화관광지정축제로 선정된 여름 대표축제 중 하나이다. 탐진강의 맑은 물, 장흥댐 호수 등 청정수자원을 기반으로 하여, 장흥의 "물=건강, 치유”이라 테마로 모든 프로그램을 연결 시켰으며, 주ㆍ야간 계속되는 다채로운 프로그램은 남녀노소를 불문하고 누구나 한여름의 무더위와 일상에서 탈출하게 해준다. 태국 송크란 축제와 이탈리아 베니스카니발 조직위원회와의 업무협약과 축제 교류로 글로벌 축제로 육성해 가는 정남진 장흥 물축제는 여름 휴가의 최고의 선택지가 되어 준다.

        2. 예시 출력: 
        5
        
        실제 입력:
        축제 이름: {festival_name}
        설명: {festival_description}
    """
    )

    festival_chain = LLMChain(llm=llm, prompt=prompt_template)



    conn = pymysql.connect(**dbconn())

    print('SQL 연결!')
    with conn.cursor(cursor=pymysql.cursors.DictCursor) as cur:
        result = cur.execute(
            """SELECT * 
            FROM tb_festival
            WHERE CategoryID is NULL""")
        festivals = cur.fetchall()

    print('input 만드는 중...')
    inputs = []
    for f in festivals:
        inputs.append({
            "festival_name": f['Name'],
            "festival_description": f['Contents'][:200],
            "festival_id": f['ID']
        })

    print('langchain 돌리는 중...')
    result = []
    batch_size=10

    for i in range(0, len(inputs), batch_size):
        batch_inputs = inputs[i: i+batch_size]

        time.sleep(2)
        print(f"{i//batch_size + 1}번째 배치 실행 중...")
        
        batch_result = festival_chain.batch(batch_inputs)
        result.extend(batch_result)
        

    print('카테고리 넣는 중...')
    for n in range(len(result)):
        with conn.cursor() as cur:
            sql = """UPDATE tb_festival 
            SET CategoryID = %s 
            WHERE ID = %s"""
            CateID = (int(result[n]['text']))
            ID = result[n]['festival_id']
            cur.execute(sql, (CateID, ID))

    conn.commit()
