# University News Scraper

This project is a script that scrapes news articles from a university website every few hours, and provides an API for querying the scraped articles by date, category, and more. The script is built using Python, Flask, and Beautiful Soup.

## Installation

To use this script, you will need to have Python 3 installed on your machine. Once you have Python installed, you can clone this repository to your local machine:

`git clone https://github.com/your-username/your-repo.git`

## Usage

To run the script, simply run the following command in your terminal:

`python app.py`

This will start a Flask server on your local machine, which you can use to query the scraped news articles.

## Requirements

To run local mongodb instance:

`docker-compose up`

## Environment variables

| Name            |                    Description                     | Requred |
| :-------------- | :------------------------------------------------: | ------: |
| MONGODB_URI     |         The URI for your MongoDB database.         |     yes |
| MONGODB_DB_NAME |    The name of the database to use in MongoDB.     |     yes |
| JWT_SECRET_KEY  | The secret key used for JSON Web Token encryption. |     yes |

### Tools

- Flask
- BeautifulSoup
- MongoDB
- Pydantic
