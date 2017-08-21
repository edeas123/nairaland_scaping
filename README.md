# nairaland_scaping
Web scraper for popular nigerian website (nairaland.com) to JSON Lines formatted text file. 

## extracted data

The data extraction pipeline was developed to aggregate data e.g. number of images in a post, number of links etc rather than extracting full text from the website. The format of the extracted data is:

    {
        _id - unique id of post/comment
        retrieved - timestamp of article scrapping
        article_id - unique article id
        forum - article forum (e.g. politics, business)
        links - number of links in comment/post
        posted- timestamp of comment/post
        quote - true or false representing if this comment quotes another one
        shares - number of times shared
        likes -  number of times liked
        images - number of images attached
        page_no - page number of the post in the article
        user - username of post writer
    }

## sample:

A sample of the extracted data can be downloaded [here](https://drive.google.com/file/d/0BzHqdm9lYwfwbGFqTWlMV0xiNnc/view?usp=sharing). A line looks like this:

    {
      "posted": "6:19am, Jul 05", 
      "links": 0, 
      "forum": "business", 
      "retrieved": "2017-08-21 02:13:03.562000", 
      "shares": 0, 
      "user": "StylixSVC", 
      "quote": false, 
      "images": 2, 
      "_id": "58136409", 
      "article_id": "3901301", 
      "page_no": 0, 
      "likes": 0
     }

The data is deliberately left unprocessed to some extent for speed in parsing as well as to give the user some data cleaning experience.

## possible analysis

There are a number of questions that can be answered using the data:

1. What is the busiest hour of the day (and day of the week) in terms of posts?
