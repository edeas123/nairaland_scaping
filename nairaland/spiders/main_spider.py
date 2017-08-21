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
        """parse the nairaland root page
        yields the top level forums for parsing"""
        root = ["nairaland"]#, "entertainment", "science"] # top level forumns
        for r in root:
            next_page = "/{0}".format(r)
            yield response.follow(next_page, self.parse_main)
        
    
    def parse_main(self, response):
        """ parse the root nairaland pages e.g nairaland, entertainment
        science"""
        
        forum = ["politics", "business"]
        for f in forum:
            next_page = "/{0}".format(f)
            request = response.follow(next_page, self.parse_forum)
            request.meta["forum"] = f

            yield request

        
    def parse_forum(self, response):
        """ parse the nairaland forum e.g. politics
        yields the next/other pages
        yields the article page. """
        
        # retrieve the number of pages in the forum
        # TODO: consider changing from hardcoding the p[4]
        page = response.xpath("//body/div/p[4]/b/text()").extract()
        
        if len(page) > 1: # there is atleast 1 or more pages (not just landing)
            # first check if its a number
            count = page[1]
            try:
                count = int(count) + 1
                for i in range(1, count):
                    next_page = "{0}/{1}".format(response.url, i)    
                    request = response.follow(next_page, self.parse_article)
                    request.meta["forum"] = response.meta['forum']
                    yield request
            except ValueError:
                count = 0
        
        for req in self.parse_article(response):
            yield req
            

    def parse_article(self, response):
        """ parse the article pages, yields the next page
         yields the article posts """
        
        # get the article title, id, url
        articles = response.xpath("//body/div[@class='body']/table[3]//td")
        articles_url = articles.xpath("b/a/@href").extract()
        #articles_titles = tds.xpath("b//a//text()").extract()

        # get the number of pages for each article        
        articles_page_count = []
        for article in articles: 
            article_pg_numbers = article.xpath("a/text()") #TODO can be improved with filtering for only href
            if len(article_pg_numbers) == 0:
                page_count = 1
            else:
                try:
                    page_count = int(article_pg_numbers[-1].extract().strip("()")) + 1 
                except ValueError:
                    page_count = 1

            articles_page_count.append(page_count)          


        # for each article, request article and call parsing function
        for a in range(len(articles_url)):
            article_url = articles_url[a]
            article_id = article_url.split("/")[1]
            #article_title = articles_titles[a]
            
            # retrieve each page of article
            for i in range(articles_page_count[a]):
                next_page = "{0}/{1}".format(article_url, i)
                request = response.follow(next_page, self.parse_posts)
                request.meta["article_id"] = article_id
                request.meta["forum"] = response.meta['forum']
                request.meta["page_number"] = i
                #request.meta["title"] = article_title
                #request.meta["pages"] = articles_page_count
                             
                yield request


    def parse_posts(self, response):
        """ parse article, retrieving relevant data from each posts"""
        
        # approximate retrieval time
        retrieved = str(datetime.datetime.now())
        
        # parse the articles posts and 
        # TODO: yield Item
        headers = response.xpath("/html/body/div[@class='body']/table[@summary='posts']//tr/td[@class='bold l pu']")
        bodys = response.xpath("/html/body/div[@class='body']/table[@summary='posts']//tr/td[@class='l w pd']")
        
        for h in range(len(headers)):
            
            header = headers[h]
            body = bodys[h]
            
            post = {}
            #post['url'] = response.url
            #post['title'] = response.meta['title']
            post['article_id'] = response.meta['article_id']
            post['forum'] = response.meta['forum']
            post['_id'] = header.xpath("a[1]/@name").extract_first()
            post['user'] = header.xpath("a[@class='user']/text()").extract_first()
            post['posted'] = ", ".join(header.xpath("span[@class='s']/b/text()").extract())     
            post['retrieved'] = retrieved
            post['page_no'] = response.meta['page_number']
            
            post['links'] = len(body.xpath("div[@class='narrow']/a/@href").extract())

            post['likes'] = 0
            likes = body.xpath("p[@class='s']/b[1]/text()").extract_first(default='').strip()
            if likes:
                post['likes'] = int(likes.split()[0])
            
            post['shares'] = 0
            shares = body.xpath("p[@class='s']/b[2]/text()").extract_first(default='').strip()
            if shares:
                post['shares'] = int(shares.split()[0])
            
            post['images'] = len(body.xpath("p/img"))
            post['quote'] = len(body.xpath("div[@class='narrow']/blockquote")) > 0
            
            yield post

 