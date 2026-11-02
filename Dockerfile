FROM python:3.11-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    TF_CPP_MIN_LOG_LEVEL=2 \
    PIP_NO_CACHE_DIR=1

# Use the CPU-only TensorFlow build for a much smaller image
COPY requirements.txt .
RUN sed 's/^tensorflow>=/tensorflow-cpu>=/' requirements.txt > req-docker.txt \
    && pip install -r req-docker.txt

COPY . .

EXPOSE 8501
HEALTHCHECK CMD python -c "import urllib.request as u; u.urlopen('http://localhost:8501/_stcore/health')"
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
