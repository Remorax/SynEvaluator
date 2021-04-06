
# SynEvaluator

A tool offering Syntactic Quality Evaluation of an ontology. Requires no programming knowledge.

This application is written in Python-Flask and deployed to Heroku [here](https://synevaluator.herokuapp.com/).

## Installation instructions

- Go the root folder of this application.
- Run `pip3 install -r requirements.txt`. 
- Then, run `export FLASK_APP=app.py` 
- Finally, run `flask run`. You should be able to access the application at http://localhost:5000/

For any help regarding how to create rules, the documentation can be accessed on [localhost](http://localhost:5000/documentation) or on the [deployed site]( https://synevaluator.herokuapp.com/documentation).

## Directory structure

This repository contains the following folders:

- `static`: For storing `js` and `css` files of the flask application 
- `templates`: For storing `html` files used in the flask application 
- `temp`: Used by the application for temporarily storing uploaded ontologies. **Please don't make any changes here**.

In addition, the root folder contains the following files:

- `app.py`: Main file of this application. Calls functions for all available routes
- `ontology.py`: Class for parsing the input ontology
- `pitfall_scanner.py`: Contains the `PitfallScanner` class that scans the ontology for any detectable pitfalls, based on the created rules.
- `helper.py`: Contains helper functions used by `pitfall_scanner.py`
- `nltk.txt`: Used by Heroku to download relevant nltk packages, in our case, WordNet.

## Help

In case any further questions are unanswered by the documentation, please don't hesitate to raise an issue.

