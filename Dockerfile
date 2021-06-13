FROM python:3.9.5

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV TZ="Asia/Kolkata"
RUN date

CMD [ "python", "./reminder_bot_driver.py" ]