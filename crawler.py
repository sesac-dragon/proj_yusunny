import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pymysql

def festival_crawler(page = None):
      # 크롤링 준비 = 최대 페이지 수 찾기
      res = requests.post('https://korean.visitkorea.or.kr/kfes/list/selectWntyFstvlList.do', 
                              data={'startIdx': '0',
                                    'searchType': 'A',
                                    'searchDate': '',
                                    'searchArea': '',
                                    'searchCate': '',
                                    'locationx': 'undefined',
                                    'locationy': 'undefined',
                                    'filterExcluded':'true'}
            )

      datas = json.loads(res.text)
      total = datas['totalCnt']
      maxpage = total//12
      
      if page is None:
            page = maxpage
      
      
      
      # print(f'축제 개수 {total} 찾기 완료')

      # sql 연결
      envs = {}
      with open('.env', 'r') as f:
            for l in f.readlines():
                  e = l.strip().split('=')
                  envs[e[0]]=e[1]


      db_config = {}
      for k, v in envs.items():
            if 'DB' not in k:
                  continue
            newk = k.split('_')[1].lower()
            if newk == 'port':
                  v = int(v)
            db_config[newk] = v


      conn = pymysql.connect(**db_config)

      print('MYSQL 연결 성공')

      # 크롤링

      fstv_total = 0

      for page in range(page+1):
            print('크롤링 중')
            n = page*12
            res = requests.post('https://korean.visitkorea.or.kr/kfes/list/selectWntyFstvlList.do', 
                              data={'startIdx': f'{n}',
                                    'searchType': 'A',
                                    'searchDate': '',
                                    'searchArea': '',
                                    'searchCate': '',
                                    'locationx': 'undefined',
                                    'locationy': 'undefined',
                                    'filterExcluded':'true'}
            )
            
            datas = json.loads(res.text)

            fstv_total += len(datas['resultList'])
            
            for data in datas['resultList']:
                  # print(data)
                  if data['fstvlBgngDe'] == '':
                        pass
                  else:
                        sdate = data['fstvlBgngDe'].replace('.', '')
                        start_date = datetime.strptime(sdate, "%Y%m%d").date()

                        edate = data['fstvlEndDe'].replace('.', '')
                        end_date = datetime.strptime(edate, "%Y%m%d").date()

                  if data['fstvlHmpgUrl'] != '':
                        text = data['fstvlHmpgUrl']
                        soup = BeautifulSoup(text, 'html.parser')
                        url = soup.select('a')
                        hmpgurl = url[0].attrs['href']
                  else:
                        hmpgurl = ''
                  
                  if 'boothInfoList' in data:
                        boothInfo = True
                  else:
                        boothInfo = False

                  print('sql로 데이터 입력 중')
                  

                  with conn.cursor() as cur:
                                    sql = """INSERT INTO tb_festival(
                                                Name, StartDate, EndDate, AreaName, Contents, 
                                                DetailContents, Address, DetailAddress, FareInfo,
                                                HomepageUrl, InstaUrl, YoutubeUrl, AspcsName,
                                                MngName, Tel, ImageUrl, OriginalID, BoothInfo)
                                                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)

                                                ON DUPLICATE KEY UPDATE 
                                                Name = VALUES(Name),
                                                StartDate = VALUES(StartDate),
                                                EndDate = VALUES(EndDate),
                                                AreaName = VALUES(AreaName),
                                                Contents = VALUES(Contents),
                                                DetailContents = VALUES(DetailContents),
                                                Address = VALUES(Address),
                                                DetailAddress = VALUES(DetailAddress),
                                                FareInfo = VALUES(FareInfo),
                                                HomepageUrl = VALUES(HomepageUrl),
                                                InstaUrl = VALUES(InstaUrl),
                                                YoutubeUrl = VALUES(YoutubeUrl),
                                                AspcsName = VALUES(AspcsName),
                                                MngName = VALUES(MngName),
                                                Tel = VALUES(Tel),
                                                ImageUrl = VALUES(ImageUrl),
                                                OriginalID = VALUES(OriginalID),
                                                BoothInfo = VALUES(BoothInfo),
                                                CategoryID = NULL;"""
                                    values =(
                                                data['cntntsNm'], start_date, end_date, data['areaNm'], 
                                                data['fstvlOutlCn'], data['fstvlCrmnCn'], data['adres'], data['dtadr'],
                                                data['fstvlUtztFareInfo'], hmpgurl, data['instaUrl'], data['ytbUrl'], data['fstvlAspcsNm'],
                                                data['fstvlMngtNm'], data['fstvlAspcsTelno'], data['dispFstvlCntntsImgRout'],
                                                data['fstvlCntntsId'], boothInfo
                                                )
                                    cur.execute(sql, values)
                                    conn.commit()
                  
      print(total, fstv_total)
      print('끝!')
