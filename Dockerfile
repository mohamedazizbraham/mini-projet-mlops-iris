FROM python:3.11-slim@sha256:07d4824036af339fa1b6ef769cc99d9c10a141769538b52b3b597c84f7a7b535
ENV PYTHONUNBUFFERED=1 PIP_DISABLE_PIP_VERSION_CHECK=1 ZENML_ANALYTICS_OPT_IN=false ZENML_ENABLE_RICH_TRACEBACK=false MPLBACKEND=Agg
RUN apt-get update && apt-get install -y --no-install-recommends git libgomp1 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.lock.txt .
RUN pip install --no-cache-dir -r requirements.lock.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
