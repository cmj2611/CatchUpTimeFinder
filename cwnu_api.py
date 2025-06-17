import requests, re

# 창원대 고정 토큰들
REST_TOKEN = 'e0610c273bcfa769cfa07aac4a8e3124'
EXTR_TOKEN = 'be1AAwtSRjkWACWbqmlzoAwUjOdeGlmV'
BEARER_TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJcYkNvdXJzZW1vcyIsImlhdCI6MTY5NzUyMzU1NiwiZXhwIjoyMDQ0NTkyNjI1LCJhdWQiOiJuYWRkbGUua3IiLCJzdWIiOiJyYWJiaXRAZGFsYml0c29mdC5jb20iLCJ1c2VyX2lkIjoiMSJ9.-799jl5c466FLKWoKld1PuOzfDb6FUHjauT-_XNVj0k'

# API 주소들
ECAMPUS_REST_URL = 'https://ecampus.changwon.ac.kr/webservice/rest/server.php'
ECAMPUS_EXTR_URL = 'https://ecampus.changwon.ac.kr/local/coursemos/extrapi/api.php'
LECTURE_PLAN_URL = 'http://chains.changwon.ac.kr/abeek/lecture_plan/view.php'

# 클래스를 쓰긴 했으나 사실 self 없이 static 메서드들만 있어서
# 메서드를 namespacing 하는 것 말고는 큰 의미 없긴함.
class CwnuApi:
    # e캠퍼스 id와 비밀번호로 로그인 함.
    def login(id, password):
        resp = requests.post(ECAMPUS_REST_URL, data = {
            'userid': id,
            'password': password,
            'wstoken': REST_TOKEN,
            'wsfunction': 'coursemos_user_login_v2',
            'moodlewsrestformat': 'json',
        })
        return resp.json()['data']

    # 학생 id로 해당 학생이 수강하고 있는 강의 목록을 가져옴.
    def get_student_courses(student_id):
        resp = requests.post(ECAMPUS_EXTR_URL, data = {
            'token': EXTR_TOKEN,
            'act': 'course_list',
            'userid': student_id,
        })
        return resp.json()['courses']
    
    # 학생 토큰과 강의 id로 수강 학생들 목록을 가져옴.
    def get_course_participants(student_token, course_id):
        resp = requests.post(ECAMPUS_REST_URL, data = {
            'courseid': course_id,
            'wstoken': student_token,
            'wsfunction': 'coursemos_course_get_participants_list_v2',
            'moodlewsrestformat': 'json',
        })
        total_count = resp.json()['data']['total_count']
        resp = requests.post(ECAMPUS_REST_URL, data = {
            'courseid': course_id,
            'wstoken': student_token,
            'ls': total_count,
            'page': '1',
            'wsfunction': 'coursemos_course_get_participants_list_v2',
            'moodlewsrestformat': 'json',
        })
        return resp.json()['data']['participants']

    # 강의 진행 시간을 가져옴.
    # course_code 예시
    # 프로그래밍입문 -> 2025_10_GEA8562_01
    def get_course_time(course_code):
        course_code_split = course_code.split('_')
        course_year = course_code_split[0]
        course_term = course_code_split[1][0]
        subject_no = course_code_split[2]
        division = course_code_split[3]
        
        resp = requests.post(LECTURE_PLAN_URL, data = {
            'year': course_year,
            'term': course_term,
            'subject_no': subject_no,
            'division': division,
            'action_mode': 'R',
        })

        # 응답 HTML에서 필요한 부분만 정규표현식으로 잘라냄
        pattern = re.escape("<td colspan=5 align=left style=\"padding-left:5\">") + "(.*?)" + re.escape("</td>")
        matched = re.search(pattern, resp.text)

        # 빈 문자는 제거함
        time_filtered = filter(lambda time: time, matched.group(1).split(','))
        # 앞 3글자만 잘라냄
        time_mapped = map(lambda time: time[0:3], time_filtered)
        return list(time_mapped)