FROM python:alpine

WORKDIR /app

COPY . .

RUN pip install --user aiogram
RUN pip install python-dotenv
RUN pip install sqlalchemy
RUN pip install asyncpg

CMD ["python", "main.py"]
