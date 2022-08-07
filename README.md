# Manga-style
Looking for inspiration as an artist? Just visit manga-style, the place to find the latest trending manga-style art on twitter.

#How it works.
What is the project structure and design?

## The Data
Using a webscraper, download images from artstation, pixiv, pinterest (sites with great digial art in manga style) to GCS. Use twitter api to get a vast assortment of current images that are not manga-style art. 

Check the data for bad data using a custom built tool.

## The Model
Apply transfer learning and fine-tune resnet to classify images as manga-style or not. After achieving satisfactory test set accuracy, deploy model to GCP and query using REST API from website. 


## The Application
Create a website using nodejs and updates state from backend server.

## Backend
Python server gets latest image twitter posts every hour and classifies as manga-style using deployed classifier. Store all trending manga-style tweets in GCP. Rank manga-style tweets and send top 100 to website.

## Notes
- Pay attention to scale
- Pay attention to model versioning
- Pay attention to clean code
- Pay attention to unit testing
- Pay attention to database
