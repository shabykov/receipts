# how to dev install

- setup environment
    - install dependencies `pip install -U -r requirements.txt`
    - up containers `docker compose up -d`
    - setup config in `.env` (database, model, etc)


- run api (HTTP REST API)
    - open `apps/api/__main__.py`
    - run `if __name__ == "__main__":`
    - open swagger `http://127.0.0.1:8080/apidocs/`

- run bot (telegram bot)
    - open `apps/bot/__main__.py`
    - run `if __name__ == "__main__":`

- run web (web app)
    - open `apps/web/__main__.py`
    - run `if __name__ == "__main__":`
