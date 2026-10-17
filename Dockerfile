FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy other root files
COPY main.py config.yml logging.yml icon.png icon_footer.png ./

# Copy the rest of the bot code
COPY bot/ ./bot/

CMD ["python", "main.py"]