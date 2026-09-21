FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    LM_STUDIO_URL=http://host.docker.internal:1234/v1/chat/completions \
    LLM_MODEL=google/gemma-3-4b

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p generated_tests results

CMD ["python", "generate_tests.py"]
