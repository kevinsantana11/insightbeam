# Insight-Beam

## Overview
The Insight Beam server should fullfill the following requirements:
* User can add sources for retrieving source items
* User can have a source item analyzed getting a general idea of the subject, points and supporting arguments being made.
* User can have a counter analysis generated for their initial analysis

## I want to run the server
* initialize a python virtual environment (for more info [visit the following link](https://docs.python.org/3/library/venv.html), I won't go into detail about this as this is out of scope for this README)
* Run the initialization command `make init` - these just copies over the `.default.env` to a `.env` file
  * The only value that needs to be filled out here is the `OPENAI_API_KEY`
* install the runtime dependencies: `pip install -r requirements.txt` 
* start the server up: `make run`

## I want to make changes to the server
* Similarly to the above, initialize a python virtual environment
* Run the initialization command `make init` - these just copies over the `.default.env` to a `.env` file
  * The only value that needs to be filled out here is the `OPENAI_API_KEY`
* install the development dependencies `pip install -r requirements.dev.txt`
* Before making any commits run `make precommit` this is going to run the following:
  * black - the formatting tool
  * flake8 - straight forward code linting
  * isort - sort those imports for consistency
  * mypy - static type analysis

