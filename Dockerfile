FROM rasa/rasa:3.6.20-full

WORKDIR /app

# Copier tout le projet sauf ce qui est ignoré
COPY . .

EXPOSE 5005

CMD ["rasa", "run", "--enable-api", "--cors", "*", "--debug"]
