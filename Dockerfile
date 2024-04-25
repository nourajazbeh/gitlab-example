FROM python:3.12.3-bookworm

LABEL Name="Flask GitLab Demo App" Version=1.0.0


WORKDIR /app
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/app ./app
CMD ["ls", "-l", "/app"]

EXPOSE 5000

CMD ["python", "app/app.py"]