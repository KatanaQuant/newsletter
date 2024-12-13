# Disclaimer

_The content and information provided by Vagabond Research, including all other materials, are for educational and informational purposes only and should not be considered financial advice or a recommendation to buy or sell any type of security or investment. Always conduct your own research and consult with a licensed financial professional before making investment decisions. Trading and investing can involve significant risk, and you should understand these risks before making any financial decisions._

# Installation

## Getting Started

Read the blogpost here: [https://katanaquant.com/blog/a-dockerized-crypto-data-hub](https://katanaquant.com/blog/a-dockerized-crypto-data-hub)

### Installation

1. Clone the repository:

```bash
git clone https://github.com/KatanaQuant/newsletter.git
```

2. Change into the project directory:

```bash
cd Issue\ 9\ -\ Dockerized\ Datalab/kq-datahub/
```

3. Create an env file containing PostgreSQL Credentials

```bash
DB_USER=postgres
DB_PW=password
DB_DB=postgres
DB_PORT=5432
```

**DISCLAIMER: This is just an example! Always use secure credentials for your environment variables (default credentials are not secure). Never store sensitive information such as passwords or API keys in your source code. Make sure to add your .env files to your .gitignore to prevent them from being tracked by version control.**

4. Build and run the application

```bash
docker compose up --build
```

5. Uncomment data-scraper service from docker-compose.yml after initial fetch

```yml
services:
  db:
    image: postgres:latest
    environment:
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PW}
      - POSTGRES_DB=${DB_DB}
    ports:
      - "${DB_PORT}:${DB_PORT}"
    volumes:
      - postgres_data:/var/lib/postgresql/data

#   data_scraper:
#     build:
#       context: ./data_scraper
#       dockerfile: Dockerfile
#     environment:
#       - DB_USER=${DB_USER}
#       - DB_PW=${DB_PW}
#       - DB_DB=${DB_DB}
#       - DB_PORT=${DB_PORT}
#     depends_on:
#       - db

volumes:
  postgres_data:
```

6. Access db via localhost:5432 when service is running
