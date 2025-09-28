# how to dev install 

- run docker 
  - docker compose up -d
  - set up database

- setup config in `.env`


- run api
  - open `apps/api/__main__.py`
  - run `if __name__ == "__main__":`
  - open swagger `http://127.0.0.1:8080/apidocs/`

- run bot
  - open `apps/bot/__main__.py` 
  - run `if __name__ == "__main__":`

- run web 
  - open `apps/web/__main__.py`
  - run `if __name__ == "__main__":`
