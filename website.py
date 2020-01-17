import string
import random
import re

import urllib
from urllib.request import urlopen, Request

from bs4 import BeautifulSoup
from googlesearch import search

AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'

class NoResultsFound(Exception):
    pass

def get_web_page_google(*argv):
    """Gerneral Google search with whatever arguments"""
    query = str(argv)
    for result in search(query, tld='com', lang='en', num=1, start=0, stop=1, pause=1):
        request = Request(result, headers={'User-Agent': AGENT})
        return BeautifulSoup(urlopen(request).read(), 'html5lib')

def get_any_webpage(url):
    """Getting user profile page"""
    r = Request(url, headers={'User-Agent': AGENT})
    return BeautifulSoup(urlopen(r).read(), 'html5lib')

class UserInfo():
    """Analysing user profile"""
    def __init__(self, soup):
        self.s = soup

    def name(self):
        return self.s.find('div', {'class':'ellipsis'}).get_text(strip=True)

    def card(self):
        e = '.png$' + ''.join(random.choice(string.ascii_lowercase) for x in range(6)) # Generate a unique URL to prevent caching issues
        return 'https://card.psnprofiles.com/1/' + self.s.find('div',{'class':'ellipsis'}).get_text(strip=True) + e

    def icon(self):
        return self.s.find('div', {'class':'avatar'}).find('img')['src']

    def description(self):
        try:
            return '"'+self.s.find('span', {'class':'comment'}).get_text(strip=True)+'"'
        except Exception:
            return # In case there is no description

class PlatinumInfo():
    """Analysing profile page"""
    def __init__(self, soup, game):
        self.s = soup
        self.u = soup.find('div', {'class':'ellipsis'}).get_text(strip=True)

        for item in self.s.find_all('tr',{'class':'platinum'}):
            if str(item.find('a',{'class':'title'}).get_text(' ', strip=True)) == game:
                self.s = item

    def name(self):
        return self.u

    def game(self):
        return self.s.find('a',{'class':'title'}).get_text(' ', strip=True)
    
    def image(self):
        return self.s.img['src']

    def description(self):
        L1 = self.s.find_all('div',{'class':'small-info'})[0].get_text(' ', strip=True) + '\n'
        L2 = self.s.find_all('div',{'class':'small-info'})[1].get_text(' ', strip=True)
        L2 = re.sub(r'\s+', ' ', L2)
        return L1+L2

    def rarity(self):
        return self.s.find('span',{'title':'Platinum Rarity'}).get_text(' ', strip=True)

class TrophiesInfo():
    """Analysing trophies page"""
    def __init__(self, soup):
        self.s = soup

    def url(self):
        return 'https://psnprofiles.com' + self.s.find('ul',{'class':'navigation'}).find('a')['href']

    def name(self):
        return self.s.find('span', {'class':'breadcrumb-arrow'}).next_sibling

    def trophies(self):
        return self.s.find('td', {'style':'padding: 10px'}).span.get_text(' ', strip=True)

    def image(self):
        A = self.s.find('div', {'id':'first-banner'}).find('div',{'class':'img'})['style']
        return A[A.find('(')+1 : A.find(')')]

    def comp(self): # The most complicated one since the completion is often displayed differently between games
        B = self.s.find('span', text='100% Completed').previous_sibling
        
        if self.s.find('li', {'class':'icon-sprite platinum'}).get_text() == '1':
            A = self.s.find('span', text='Platinum Achievers').previous_sibling
        
        if self.s.find('li', {'class':'icon-sprite platinum'}).get_text() == '0':
            A = '0'
                
        if A[A.find('(')+1 : A.find(')')] == B[B.find('(')+1 : B.find(')')]:
            A = A[A.find('(')+1 : A.find(')')]
            return f' • {A}'
        
        if '(' in A and '(' in B:
            A = A[A.find('(')+1 : A.find(')')]
            B = B[B.find('(')+1 : B.find(')')]
            return f' • {A} ({B})'
        
        if '(' in A and '(' not in B:
            B = A[A.find('(')+1 : A.find(')')]
            return f' • {B} (0%)'
        
        if '(' not in A and '(' in B:
            B = B[B.find('(')+1 : B.find(')')]
            return f' • {B}'
        
        else:
            return ' • 0%' # In case no one 100%'d nor platinum'd the game

    def guide(self):
        try:
            url = 'https://psnprofiles.com' + self.s.find('ul',{'class':'navigation'}).find('a')['href'].replace('trophies','guides')
            searchsoup = BeautifulSoup(urlopen(url).read(), 'html5lib')
            url2 = 'https://psnprofiles.com'+searchsoup.find('div',{'class':'guide-page-info'}).find('a')['href']
            guidesoup = BeautifulSoup(urlopen(url2).read(), 'html5lib')
            dif = guidesoup.find('div',{'class':'overview-info'}).find_all('span')[0].get_text(' ', strip=True)
            plays = guidesoup.find('div',{'class':'overview-info'}).find_all('span')[3].get_text(' ', strip=True)
            hours = guidesoup.find('div',{'class':'overview-info'}).find_all('span')[6].get_text(' ', strip=True)
            return dif + ' | ' + plays + ' | ' + hours
            
        except Exception:
            return '' # In case there is no guide

"""    SEARCH THROUGH PSPRICES DIRECTLY:
    url = 'https://psprices.com/region-us/search/?q={}&platform=PS4&dlc=hide'.format(game.replace(' ','+'))
    r = Request(url, headers={'User-Agent': AGENT})
    page = BeautifulSoup(urlopen(r).read(), 'html5lib')
    if page.find('div', {'class':'content__cat__pre_title'}) != None:
        result = 'https://psprices.com'+page.find('div',{'class':'col-md-2 col-sm-3 col-xs-6'}).a['href']
        r2 = Request(result, headers={'User-Agent': AGENT})
        return BeautifulSoup(urlopen(r2).read(), 'html5lib')
    else:
        return page"""

class PriceInfo():
    """Analysing game price page"""
    def __init__(self, soup):
        self.s = soup
    
    def page_url(self):
        return self.s.find('meta', {'property':'og:url'})['content']

    def title(self):
        return self.s.find('div', {'class':'col-md-9'}).find('h1').contents[0].strip()
    
    def store_url(self):
        return self.s.find('div', {'class':'col-xs-12 col-sm-6'}).find('a')['href']

    def price(self):
        return self.s.find('div', {'class':'col-xs-12 col-sm-6'}).find('span',{'class':'current'}).get_text(strip=True)

    def plus_price(self):
        try:
            A = self.s.find('div', {'class':'col-xs-12 col-sm-6'}).find('span',{'class':'plus'}).get_text(strip=True)
            return f' ({A})'
        except Exception:
            return '' # In case there is no PLus Price
    
    def lowest_price(self):
        return self.s.find('div', {'id':'price_history'}).strong.next_sibling.next_sibling.get_text(strip=True)

    def image(self):
        return self.s.find('div', {'class':'content__game_card__cover'}).find('img')['data-src']

"""    SEARCH THROUGH METACRITIC DIRECTLY:
    url = 'https://www.metacritic.com/search/game/{}/results'.format(game.replace(' ','+'))
    r = Request(url, headers={'User-Agent': AGENT})
    page = BeautifulSoup(urlopen(r).read(), 'html5lib')
    result = 'https://www.metacritic.com'+page.find('h3',{'class': 'product_title basic_stat'}).a['href']
    r2 = Request(result, headers={'User-Agent': AGENT})
    return BeautifulSoup(urlopen(r2).read(), 'html5lib')"""

class MetaInfo():
    """Analysing Metacritic page"""
    def __init__(self, soup):
        self.s = soup

    def chech_result(self):
        return type(self.s)

    def title(self):
        return self.s.find('div',{'class':'product_title'}).h1.get_text(strip=True)

    def url(self):
        return 'https://www.metacritic.com' + self.s.find('div',{'class':'product_title'}).a['href']

    def image(self):
        return self.s.find('img',{'class':'product_image large_image'})['src']

    def score(self):
        return "**" + self.s.find('a',{'class':'metascore_anchor'}).get_text(strip=True) + "**"

    def critics(self):
        return self.s.find('span',{'class':'based'}).next_element.next_element.next_element.get_text(' ', strip=True)

    def best_review_author(self):
        return 'Best Review, by '+self.s.find('li',{'class':'review critic_review first_review'}).find('div',{'class':'source'}).get_text(strip=True)

    def best_review_body(self):
        return '"'+self.s.find('li',{'class':'review critic_review first_review'}).find('div',{'class':'review_body'}).get_text(strip=True)+'"'

    def worst_review_author(self):
        return 'Worst Review, by '+self.s.find('li',{'class':'review critic_review last_review'}).find('div',{'class':'source'}).get_text(strip=True)

    def worst_review_body(self):
        return '"'+self.s.find('li',{'class':'review critic_review last_review'}).find('div',{'class':'review_body'}).get_text(strip=True)+'"'

    def color(self):
        X = int(self.s.find('a',{'class':'metascore_anchor'}).get_text(strip=True))
        if X >= 75:
            return 0x66CC33
        if X <= 74 and X >= 50:
            return 0xffcc33
        if X <= 49:
            return 0xFF0000

class HowLongInfo():
    """Analysing HowLongToBeat page"""
    def __init__(self, soup):
        self.s = soup

    def title(self):
        return self.s.find('div',{'class':'profile_header shadow_text'}).get_text(' ', strip=True)

    def url(self):
        return 'https://howlongtobeat.com/' + self.s.find('div',{'class':'content_75_static scrollable back_clear'}).a['href']

    def image(self):
        return self.s.find('img',{'alt':'Box Art'})['src']

    def times(self): # Find all "game_times" classes and display them line after line
        X = ''
        for item in self.s.find('div',{'class':'game_times'}).find_all('li'):
            X += str(item.find_all('h5'))+': '
            X += '**'+str(item.find_all('div'))+'**\n'

        X = BeautifulSoup(X, 'html5lib').get_text('', strip=True).replace('[','').replace(']','')
        return X