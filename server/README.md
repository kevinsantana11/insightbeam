# Insight-Beam

## Overview
The Insight Beam server should fullfill the following requirements:
* User can add sources for retrieving source items
* User can have a source item analyzed getting a general idea of the subject, points and supporting arguments being made.
* User can have a counter analysis generated for their initial analysis

Should be noted for the moment the server really works with the `Happy Path` edge cases and good error handling haven't been implemented as of yet.

## I want to run the server
### Base Setup
* Run the initialization command `make init` - this does the following:
  * copies over the `.default.env` to a `.env` file
  * Makes a `data/server` directory where the containers data folder is mounted to so that we can view the logs and easily check the sqlite db.
  * Deletes a `sqlite.db` file if found
* The only value that needs to be filled out in the .env file is the `OPENAI_API_KEY`
### Via your local environment (this assumes you have python3.9+ installed)
* (optional but, recommended) initialize a python virtual environment (for more info [visit the following link](https://docs.python.org/3/library/venv.html), I won't go into detail about this as this is out of scope for this README)
* install the runtime dependencies: `pip install -r requirements.txt` 
* start the server up: `make run`
### Via Docker Compose
* docker-compose build && docker-compose up

## I want to make changes to the server
* Follow the instruction in the `Base Setup`
* install the development dependencies `pip install -r requirements.dev.txt`
* Before making any commits run `make precommit` this is going to run the following:
  * black - the formatting tool
  * flake8 - straight forward code linting
  * isort - sort those imports for consistency
  * mypy - static type analysis

