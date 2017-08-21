# -*- coding: utf-8 -*-
"""
Created on Wed Aug 09 05:41:53 2017

@author: oodiete
"""

import scrapy
import datetime

class MainSpider(scrapy.Spider):

    name = "nairaland"
    start_urls = ["http://www.nairaland.com"]
    
    def parse(self, response):
        # parse the nairaland root page
        # yields the different forums for parsing
        # TODO: parse forum downward
        #yield response.follow("/politics", self.parse_forum)
        root = ["nairaland", "entertainment", "science"]
        for r in root:
            next_page = "/{0}".format(r)
            yield response.follow(next_page, self.parse_main)
        
    
    def parse_main(self, response):
        """ parse the root nairaland pages e.g nairaland, entertainment
        science"""
        
        forum = ["politics", "business"]
        for f in forum:
            next_page = "/{0}".format(f)
            request = response.follow(next_page, self.parse_main)
            request.meta["forum"] = f

            yield request
        
    def parse_forum(self, response):
        """ parse the nairaland forum e.g. politics
        yields the next/other pages
        yields the article page. """
        
        # retrieve the number of pages in the forum
        page = response.xpath("//body//div//p[4]//b//text()").extract()
        requests_list = []
        
        if len(page) > 1: # there is atleast 1 or more pages
            # first check if its a number
            count = page[1]
            try:
                count = int(count) + 1
                for i in range(count):
                    next_page = "{0}/{1}".format(response.url, i)                    
                    requests_list.append(response.follow(next_page, self.parse_article))
            except ValueError:
                count = 0

        return requests_list
    
    def parse_article(self, response):
        # parse the article pages
        # yields the next page
        # yields the article posts
        
        # TODO: parse the article's landing page (page 0)
        requests_list = []

        tds = response.xpath("//body//table[3]//td")
        articles = tds.xpath("b//a//@href").extract()
        #articles_titles = tds.xpath("b//a//text()").extract()
        articles_page_count = []
        
        for td in tds: 
            tdl = td.xpath("a//text()")
            if len(tdl) == 0:
                pg = 1
            else:
                try:
                    pg = int(tdl[-1].extract().strip("()")) + 1
                except ValueError:
                    pg = 1
            
            articles_page_count.append(pg)          
            
        if len(articles) > 1:
            for a in range(len(articles)):
                article_url = articles[a]
                article_id = article_url.split("/")[1]
                #article_title = articles_titles[a]
                
                for i in range(articles_page_count[a]):
                    next_page = "{0}/{1}".format(article_url, i)
                    req = response.follow(next_page, self.parse_posts)
                    req.meta["article_id"] = article_id
                    #req.meta["title"] = article_title
                    #req.meta["pages"] = articles_page_count
                                 
                    requests_list.append(req)

        return requests_list
        
    
    def parse_posts(self, response):
        
        # approximate retrieval time
        retrieved = str(datetime.datetime.now())
        
        # parse the articles posts and yield Item
        tds = response.xpath("//html//body//div//table[@summary='posts']//tr//td[@class='bold l pu']")
        posts = []
        # TODO: use article id instead of full url
        # TODO: comment out the title entry, also to save space and not really necessary
        for td in tds:
            post = {}
            #post['url'] = response.url
            #post['title'] = response.meta['title']
            post['article_id'] = response.meta['article_id']
            post['_id'] = td.xpath("a[1]/@name").extract_first()
            post['user'] = td.xpath("a[@class='user']//text()").extract_first()
            post['posted'] = ", ".join(td.xpath("span[@class='s']//b//text()").extract())     
            post['retrieved'] = retrieved
            posts.append(post)

        return posts
   