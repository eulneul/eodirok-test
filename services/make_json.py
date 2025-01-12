import re
from datetime import datetime

def parse_date(date_str):
    # 날짜와 시간을 포함한 문자열 (예: 2024년 12월 25일 수요일 오후 5:31)
    date_match = re.search(r'(\d{4}년 \d{1,2}월 \d{1,2}일)', date_str)
    time_match = re.search(r'(오후 \d{1,2}:\d{2})|(오전 \d{1,2}:\d{2})', date_str)
    
    if date_match:
        # 정확히 공백을 제거하고 '-'로 포맷
        date = date_match.group(1).replace("년", "-").replace("월", "-").replace("일", "").strip()
        date = re.sub(r'\s+', '', date)  # 모든 불필요한 공백 제거
    else:
        # "오늘"을 현재 날짜로 변환
        today = datetime.today()
        date = today.strftime('%Y-%m-%d')
    
    if time_match:
        time_str = time_match.group(0).replace("오후", "").replace("오전", "").strip()
        hour, minute = map(int, time_str.split(":"))
        
        # 오후일 경우 시간을 12시간 더함
        if "오후" in time_match.group(0) and hour != 12:
            hour += 12
        if "오전" in time_match.group(0) and hour == 12:
            hour = 0
        
        # 정상적인 타임스탬프 반환
        return f"{date}T{hour:02}:{minute:02}:00"
    
    # 시간 정보가 없을 경우 기본 시간 00:00:00 사용
    return f"{date}T00:00:00"

def parse_text(text):
    lines = text.splitlines()
    tasks = []
    date_str = None
    task_description = ""
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        # 날짜 및 시간 정보를 포함한 줄에서 날짜 추출
        if "오늘" in line or re.search(r'\d{4}년 \d{1,2}월 \d{1,2}일', line):
            date_str = parse_date(line)
        
        # "이(가)"가 포함된 문장에서 작업을 추출
        if "이(가)" in line:
            if i + 2 < len(lines):
                task_description = lines[i+2].strip()
                tasks.append({
                    "name": f"Task {len(tasks) + 1}",
                    "description": task_description,
                    "project_at": date_str  # 추출된 날짜 사용
                })
                task_description = ""  # reset for next task
    
    return tasks


# 입력 텍스트
text = """
2024년 12월 25일 수요일 오후 5:31

김 민아이(가) 만든 안녕하세요! 고객사로부터 전달받은 데이터와 관련하여, 통합과 전처리를 진행하였...
김 민아
안녕하세요! 고객사로부터 전달받은 데이터와 관련하여, 통합과 전처리를 진행하였습니다! 감사합니다!

오늘 오후 5:10
김민아이(가) 만든 안녕하세요! 데이터 전처리표와 관련하여 오류 사항이 있어서, 수정 진행하였습니...
김민아
안녕하세요! 데이터 전처리표와 관련하여 오류 사항이 있어서, 수정 진행하였습니다!
"""

# 결과 확인
tasks = parse_text(text)

import json
print(json.dumps(tasks, ensure_ascii=False, indent=4))
