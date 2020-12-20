import string
import random
import re
import pyshorteners

import urllib
from urllib.request import urlopen, Request

from bs4 import BeautifulSoup
from googlesearch import search

AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'


def link_shortener(url):
    s = pyshorteners.Shortener()
    return s.tinyurl.short(url)

class NoResultsFound(Exception):
    pass

class CommandUnusable(Exception):
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
    def __init__(self, soup):
        self.g = soup.find(text='Latest Platinum').find_previous('a').get_text(strip='True')
        self.s = soup.find('div', {'class':'box no-top-border'}).find(text=self.g).find_previous('tr',{'class':'platinum'})
        self.u = soup.find('span',{'class':'username'}).get_text(strip=True)
        self.c = False

        if 'earned' in soup.find('div', {'class':'box no-top-border'}).find(text=self.g).find_next('span', {'class':'separator completion-status'}):
            self.c = True


    def name(self):
        return self.u

    def game(self):
        return self.g
    
    def image(self):
        return self.s.img['src']

    def url(self):
        return 'https://psnprofiles.com'+self.s.find('a',{'class':'title'})['href']

    def description(self):
        L1 = self.s.find_all('div',{'class':'small-info'})[0].get_text(' ', strip=True)
        L2 = self.s.find_all('div',{'class':'small-info'})[1].get_text(' ', strip=True)
        L2 = re.sub(r'\s+', ' ', L2)

        if self.c == True:
            return L1+', Platinum and 100% completion!\n'+L2

        else:
            return L1+'\n'+L2

    def rarity(self):
        if self.c == True:
            return self.s.find('span',{'title':'Completion Rate'}).get_text(' ', strip=True)

        if self.c == False:
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
        
        if self.s.find('li', {'class':'icon-sprite platinum'}).get_text() == '1' and self.s.find('span', text='Platinum Achievers') != None:
            A = self.s.find('span', text='Platinum Achievers').previous_sibling
            
        if self.s.find('li', {'class':'icon-sprite platinum'}).get_text() == '1' and self.s.find('span', text='Platinum Achievers') == None:
            A = self.s.find('span', text='Platinum Achiever').previous_sibling
        
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
        if self.s.find('div', {'class':'guide-page-info sm'}) == None:
            return '' # In case there is no guide
        
        url = 'https://psnprofiles.com' + self.s.find('div', {'class':'guide-page-info sm'}).a['href']
        guidesoup = BeautifulSoup(urlopen(url).read(), 'html5lib')
        X = guidesoup.find('div', {'class':'overview-info'}).find_all('span', {'class':'tag'})
        return f"{X[0].get_text(' ', strip=True)} | {X[1].get_text(' ', strip=True)} | {X[2].get_text(' ', strip=True)}"

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

        """ Four options in which price is displayed:
        0: No sale at all (NAL)
        1: On sale with plus special price (PLUS)
        2: On sale with no plus special price (SALE)
        """
        status = soup.find('td', {'class':'w-100'})

        if status.find('span', {'class':'old_price h5 mx-1'}) != None:
            self.sale = 2

        elif status.find('span', {'class':'content__game_card__price_plus h5'}) != None:
            self.sale = 1

        else:
            self.sale = 0

    def page_url(self):
        return self.s.find('meta', {'property':'og:url'})['content']

    def title(self):
        return self.s.find('div', {'class':'content__game__title d-block my-0'}).h2.get_text(strip=True)
    
    def store_url(self):
        return self.s.find('td', {'class':'w-100'}).find('a')['href']

    def price(self):

        if self.sale == 2:
            a = self.s.find('td', {'class':'w-100'}).find('a').get_text(strip=True)
            b = self.s.find('span', {'class':'old_price h5 mx-1'}).get_text(strip=True)
            return f'On Sale: {a} | ~~{b}~~'

        if self.sale == 1:
            a = self.s.find('span', {'class':'content__game_card__price_plus h5'}).get_text(strip=True)
            b = self.s.find('td', {'class':'w-100'}).find('a').get_text(strip=True)
            return f'Current Price {b} | **Plus: {a}**'

        if self.sale == 0:
            a = self.s.find('td', {'class':'w-100'}).find('a').get_text(strip=True)
            return f'Current Price: {a} (Not on sale)'
    
    def lowest_price(self):
        return 'Lowest Price: ' + self.s.find('div', {'id':'price_history'}).strong.next_sibling.next_sibling.get_text(strip=True)

    def image(self):
        return self.s.find('div', {'class':'d-flex force-scroll game--media'}).a['href']

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

        try:
            int(self.s.find('a',{'class':'metascore_anchor'}).get_text(strip=True))

        except (ValueError, AttributeError):
            raise NoResultsFound()

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
        x = '"'+self.s.find('li',{'class':'review critic_review first_review'}).find('div',{'class':'review_body'}).get_text(strip=True)+'"'
        if len(x) <= 400:
            return x
        if len(x) >= 400:
            return ' '.join(x[:400+1].split(' ')[0:-1]) + '..."'

    def worst_review_author(self):
        return 'Worst Review, by '+self.s.find('li',{'class':'review critic_review last_review'}).find('div',{'class':'source'}).get_text(strip=True)

    def worst_review_body(self):
        x = '"'+self.s.find('li',{'class':'review critic_review last_review'}).find('div',{'class':'review_body'}).get_text(strip=True)+'"'
        if len(x) <= 400:
            return x
        if len(x) >= 400:
            return ' '.join(x[:400+1].split(' ')[0:-1]) + '..."'

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

class PSStoreInfo():

    def __init__(self, soup):
        self.s = soup

    def slides_count(self):
        X = str(self.s.find('div', {'class':'slideshow-controls__pager'}))
        return int(X.count('carousel-dots__nav-dot')) - 2

    def url(self, num):
        if 'https' not in self.s.find('div',{'class':'slideshow-banner'}).find_all('span')[num].a['href']:
            return 'https://store.playstation.com' + self.s.find('div',{'class':'slideshow-banner'}).find_all('span')[num].a['href']

        else:
            return self.s.find('div',{'class':'slideshow-banner'}).find_all('span')[num].a['href']

    def image(self, num):
        return self.s.find('div',{'class':'slideshow-banner'}).find_all('img')[num]['src']

class PSNews():

    def __init__(self, soup):
        self.s = soup.find('div',{'class':'bl_la_main'})

    def all_news(self):
        x = ''
        count = 0
        for item in self.s.find_all('div',{'class':'newsTitle'}):
            x += '**● ' + item.get_text(strip=True) + '**'
            x += '\n'
            x += link_shortener('https://www.playstationtrophies.org' + item.a['href'])
            x += '\n\n'
            count += 1
            if count == 5:
                break
        return x

