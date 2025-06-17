from os import system
from cwnu_api import CwnuApi

id = input('E캠퍼스 아이디: ')
password = input('E캠퍼스 패스워드: ')
system('clear||cls') # 출력창 클리어

# 로그인 후 본인이 듣는 강의 목록 가져옴.
my_data = CwnuApi.login(id, password)
my_courses = CwnuApi.get_student_courses(my_data['id'])

# 숫자랑 강의 대응 시켜서 출력함.
print('보강 시간을 찾으려는 강의를 선택하세요.\n')
for idx, course in enumerate(my_courses):
    print(f'{idx}: {course['fullname']}')
print()

# 숫자 입력 받아서 대응되는 강의의 수강생 목록 가져옴.
selected_course = int(input('강의 번호: '))
system('clear||cls') # 출력창 클리어
course_participants = CwnuApi.get_course_participants(my_data['utoken'], my_courses[selected_course]['id'])

# 수강생들 각각의 시간표 가져와서 집합 자료형에 집어 넣음
# 집합 특성상 자동으로 중복되는 강의는 제거됨.
course_set = set()
current = 0
for participant in course_participants:
    current += 1
    print(f'수강정보 처리 중 [{current}/{len(course_participants)}]: {participant['fullname']}')
    print('\033[1A', end='\x1b[2K') # 출력할 때 다음 줄로 넘기지 않고 기존의 줄을 덮어씌움.
    participant_courses = CwnuApi.get_student_courses(participant['id'])
    for participant_course in participant_courses:
        course_set.add((participant_course['course_code'], participant_course['fullname']))

# 강의 집합 속 강의들의 진행 시간을 가져와서 마찬가지로 집합 자료형에 넣음.
# 간단히 말해서 course_time_set에는 보강 불가능한 시간들이 모두 저장돼 있음.
course_time_set = set()
current = 0
for course_code, course_name in course_set:
    current += 1
    print(f'강의정보 처리 중 [{current}/{len(course_set)}]: {course_name}')
    print('\033[1A', end='\x1b[2K') # 출력할 때 다음 줄로 넘기지 않고 기존의 줄을 덮어씌움.
    course_times = CwnuApi.get_course_time(course_code)
    for course_time in course_times:
        course_time_set.add(course_time)

system('clear||cls') # 출력창 클리어

# 완전한 강의 시간표 생성.
timetable_set = set()
for weekday in ['월', '화', '수', '목', '금']:
    for hour in range(1, 10):
        for part in ['A', 'B']:
            timetable_set.add(f'{weekday}{hour}{part}')

# 완전한 강의 시간표 집합에서 보강 불가능 시간 집합을 뺌.
# catch_up_time_set에는 보강 '가능' 시간만 남음.
catch_up_time_set = timetable_set - course_time_set

if len(catch_up_time_set) == 0:
    # 보강 가능한 시간 없으면 없다고 출력.
    print(f'\'{my_courses[selected_course]['fullname']}\' 강의는 평일 정상 시간에 보강할 수 없습니다.')
else:
    # 집합 자료형은 저장하는 자료에 순서 개념이 없기 때문에,
    # 리스트로 변환하고 정렬해서 시간을 읽기 편하게 만들어줌.
    catch_up_times = sorted(list(catch_up_time_set))
    # 보강 가능한 시간 출력.
    print(f'\'{my_courses[selected_course]['fullname']}\' 강의는 {catch_up_times}에 보강 가능합니다!')