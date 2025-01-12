# Python 베이스 이미지 선택
FROM python:3.9

# 필요한 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    libpq-dev gcc \
    openjdk-17-jdk \
    && rm -rf /var/lib/apt/lists/*

# 환경 변수 설정
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="$JAVA_HOME/bin:$PATH"

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . /app/

# Gunicorn으로 앱 실행
CMD ["gunicorn", "-w", "4", "-k", "sync", "-b", "0.0.0.0:5000", "app:create_app()"]

