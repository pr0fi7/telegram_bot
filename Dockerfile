FROM python:3.9-slim

WORKDIR /app

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your source code
COPY . .

# Expose the port if your bot listens on one (optional)
EXPOSE 8080

# Command to run your bot, adjust as needed.
CMD ["python", "main.py"]
