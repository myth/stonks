FROM node:16-alpine

WORKDIR /app

ADD stonks/dashboard/package.json stonks/dashboard/package-lock.json ./
RUN npm i
COPY stonks/dashboard/ ./
RUN npm run build

FROM python:3.9-slim

WORKDIR /app

ADD requirements.txt .
RUN pip3 install -r requirements.txt && rm -rf stonks/dashboard
ADD main.py .
COPY stonks ./stonks
COPY --from=0 /app/build /app/stonks/dashboard/build

EXPOSE 8080

CMD ["python", "main.py", "-c", "/app/config.json", "--db", "/app/history.db"]
