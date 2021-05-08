# Hiking Trail Recommender
Capstone Project of Lighthouse Labs consisting of web scraping hiking trail information to build a dataset on top of the Walking and Tramping routes provided by the Department of Conservation (DOC) in New Zealand. Trail information is cleaned and recommendation systems are generated based on hiking similarities. If possible, user reviews of the tracks will be included as well as images of the trail for a multiple recommendation offers during deployment.

## Project Decription
One of the biggest limitations getting into hiking is knowing which trail to pick. Often times, the common resources we have for trail information are catagorized by location-- which park is nearby and then search trails within. But if you're new to the activity or looking to branch out of your nearby park, a recommonder system that finds similar trail difficulties and popularity based on your activity level is ideal. 

## Project Setup
This github repo will contain all the information I am assembling to generate this recommendation system. 

Data: I have started with the [Walking and Tramping Routes provided by the Department of Conservation (DOC)](https://doc-deptconservation.opendata.arcgis.com/datasets/e3f63067394a46238c92f9aed63ff78b), a New Zealand government agency dedicated to conserving New Zealand’s natural and historic heritage. With this, I have 3000+ trail routes across NZ. I've chosen to work in NZ by personal preference as it is one of the best countries to go explore the great outdoors. I will be supplementing this information using BeautifulSoup and/or Selenium Chromedriver to scrape trail information and user review websites to generate further track information. First I will look for website resources that provide track information. Then user reviews. Time permitting, I hope to scrape an inventory of photos for these trails to offer a visual element to the recommender system(s).

Machine Learning: I intend to first generate a content-based filtering recommendation system using hike to hike similarities. This model will look at trail length, elevation, difficulties, etc. Secondly, once user review information has been cleaned and preprocessed, I want to generate two further recommender engines. The first will encapsulate the most popular trails overall, as people often are drawn to popular sites for a reason. The second collaborative filtering model will generate similarly liked hikes based on input hike. If I am able, the final stretch goal I set for myself is to include an image repository such that users can pick a trail they like based on pictures and give back trail recommendations based on this.

## Project Milestone
Milestone | Deadline | Actual | Notes |
--- | --- | --- | --- |
Project Started | May 6 | May 6 | Started off rough but decided to pursue NZ hikes |
Data Gathered | May 9 | | |
Dataset Prepared | May 10 | | |
Content-Based Recommender | May 10 | | |
Popular Trail Recommender | May 11 | | |
User-Based Recommender | May 12 | | |
Flask API App | May 14 | | |
Image Data Exploration | May 15 | | |
Image Recommender | May 16 | | |
Deployment | May 16 | | |
Presentation Started | May 17 | | |
Presentation Dry-Run | May 19 | | |
Presentation | May 20 | | |

## Progress Report - Daily
The following will be updated through-out the duration of this capstone project to reflect the progress made
##### Thurs May 6, 2021
* Tasks: Find trail information to build the dataset from
* Accomplished: DOC Routes obtained. WalkingKiwi.co.nz identified as scrapable for trail information.
* Hurdles: Web scraping and parsing through the soup to get information useful to me. Need to find user information.

##### Fri May 7, 2021
* Tasks: Setup Github repo information. Scrape and transform WalkingKiwi trail information. Clean. Find user reviews of trails.
* Accomplished: 
* Hurdles:

