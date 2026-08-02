# 프로덕션 배포용 (Render/Railway/Fly.io 등 Docker 지원 Python 호스팅 공용).
FROM python:3.12-slim

WORKDIR /app

# chromadb/fastembed의 일부 의존성(hnswlib 등)이 빌드 도구를 필요로 함
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# SQLite/ChromaDB/fastembed 캐시가 저장될 디렉토리 - 호스팅에 영구 디스크가
# 있다면 이 경로를 마운트해야 재배포 후에도 데이터가 유지된다.
RUN mkdir -p /app/data
ENV FASTEMBED_CACHE_DIR=/app/data/.cache/fastembed

EXPOSE 8000

# 호스트가 지정하는 $PORT를 사용(Render/Railway 표준), 없으면 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
