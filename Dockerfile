FROM python:3.9-slim 
ENV PYTHONDONTWRITEBYTECODE 1 
ENV PYTHONUNBUFFERED 1 
ENV PIP_NO_CACHE_DIR 1 
WORKDIR /app 
RUN apt-get update && apt-get install -y --no-install-recommends gcc python3-dev && rm -rf /var/lib/apt/lists/* 
COPY requirements.txt . 
RUN python -m pip install --user --no-cache-dir -r requirements.txt 
COPY . . 
RUN if [ -f "/root/.local/bin/python" ]; then ln -s /root/.local/bin/python /usr/local/bin/apppython; fi 
CMD ["python", "testec.py"] 
