FROM python:3.12-slim
WORKDIR /app
COPY . /app

# System dependencies
RUN apt-get update && apt-get install -y \
    gcc g++ coinor-cbc \
    xclip xsel \
    && rm -rf /var/lib/apt/lists/*

# Packages installation
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501
CMD ["streamlit", "run", "main.py"]