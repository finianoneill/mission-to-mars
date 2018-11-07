# import dependencies
from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import datetime as dt

# create function based on 1) in Jupyter Notebook
def mars_news_scrape(browser):

    # Assign URL variables to visit the NASA website
    nasa_url = 'https://mars.nasa.gov/news/'
    # have Chrome navigate to that URL
    browser.visit(nasa_url)

    # Get first list item and wait half a second if not immediately present
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=0.5)

    # Convert the browser html from the NASA website from the link above to a Beautiful Soup object
    nasa_html = browser.html
    nasa_beautiful_soup = BeautifulSoup(nasa_html, 'html.parser')

    try:
        # after running through the total beautiful soup object by doing "print(nasa_beautiful_soup)"
        # and searching for the first article title I saw upon visual inspection of the page
        # ("The Mars InSight..."), I determined the news titles were in a div with class 
        # "content_title"

        # Thus, use the parent element to find the first a tag and save it as `news_title` since
        # the first tag is the latest by date
        news_title = nasa_beautiful_soup.find("div", class_='content_title').get_text()
        # The first paragraph text can be found with similar logic
        news_paragraph = nasa_beautiful_soup.find('div', class_="article_teaser_body").get_text()

    except AttributeError:
        return None, None

    return news_title, news_paragraph

# create function based on 2) in Jupyter Notebook
def featured_image_scrape(browser):

    # Visit the provided URL in Chrome to scrape for the images
    JPL_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(JPL_url)

    # After inspecting the page using it was determined that the full image button has
    # id = "full_image", thus we use Splinter to find that id
    JPL_full_image_elem = browser.find_by_id('full_image')

    # instruct Chrome to click the full image button
    JPL_full_image_elem.click()

    # After inspecting the subsequent page, it is determine
    # that the "More Info" button needs to be pressed to get access to the 
    # full image. After inspection, the <a> element class is "button". Since that is generic,
    # use the text within the button to click it.
    browser.is_element_present_by_text("more info", wait_time=0.5)
    JPL_more_info_elem = browser.find_link_by_partial_text('more info')
    JPL_more_info_elem.click()

    # Now that we are on the page with the full image we need to parse html with BeautifulSoup
    # to get the image link and store it to a variable
    JPL_html = browser.html
    JPL_img_soup = BeautifulSoup(JPL_html, 'html.parser')

    try:
        # find the relative image url. After page inspection it is determined the image is within an
        # <img> element with class "main_image" nested within a figure with class "lede"
        JPL_img_url_rel = JPL_img_soup.select_one('figure.lede a img').get("src")

    except AttributeError:
        return None

    # Use the base url to create an absolute url
    JPL_base_URL = "https://www.jpl.nasa.gov"
    JPL_absolute_img_url = JPL_base_URL + JPL_img_url_rel

    return JPL_absolute_img_url

# create function based on 3) in Jupyter Notebook
def twitter_weather_scrape(browser):

    # have the Chrome browser navigate to the provided Twitter URL
    mars_twitter_url = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(mars_twitter_url)

    # parse the resultant HTML with Beautiful Soup
    mars_twitter_html = browser.html
    mars_weather_soup = BeautifulSoup(mars_twitter_html, 'html.parser')

    # First, find a tweet with the data-name `Mars Weather`
    mars_weather_tweet = mars_weather_soup.find('div', attrs={"class": "tweet", "data-name": "Mars Weather"})

    # Next, search within the tweet for the p tag containing the tweet text
    found_mars_weather = mars_weather_tweet.find('p', 'tweet-text').get_text()

    return found_mars_weather

# create function based on 4) in Jupyter Notebook
def mars_facts():
    try:
        df = pd.read_html("http://space-facts.com/mars/")[0]
    except BaseException:
        return None

    df.columns = ["description", "value"]
    df.set_index("description", inplace=True)

    # Add some bootstrap styling to <table>
    return df.to_html(classes="table table-striped")

# create function based on 5) in Jupyter Notebook
def hemispheres_scrape(browser):

    # navigate to the USGS site with the link provided in the Chrome browser
    USGS_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(USGS_url)

    # instantiate an empty list to hold all of the scraped image urls
    hemisphere_image_urls = []

    # Then, get a list of all of the hemispheres
    hemisphere_links = browser.find_by_css("a.product-item h3")

    # Next, loop through those links, click the link, find the sample anchor, and return the href
    for i in range(len(hemisphere_links)):
        # create an empty dictionary
        current_hemisphere = {}
        
        # We have to find the elements on each loop to avoid a stale element exception
        browser.find_by_css("a.product-item h3")[i].click()
        
        try:
            # Next, we find the Sample image anchor tag and extract the href
            sample_elem = browser.find_link_by_text('Sample').first
            # set the href into the dictionary
            current_hemisphere['img_url'] = sample_elem['href']

        except AttributeError:
            # Image error returns None for better front-end handling
            current_hemisphere['img_url'] = None
        
        try:
            # Get the Hemisphere title and place it in the dictionary
            current_hemisphere['title'] = browser.find_by_css("h2.title").text

        except AttributeError:
            current_hemisphere['title'] = None
        
        # Append hemisphere dictionary to the list
        hemisphere_image_urls.append(current_hemisphere)
        
        # Finally, we navigate backwards in the browser so that on the next iteration the images
        # can be clicked into
        browser.back()

    return hemisphere_image_urls




def scrape_all():

    # Initiate Chrome driver
    browser = Browser("chrome", executable_path="chromedriver", headless=True)
    news_title, news_paragraph = mars_news_scrape(browser)

    # Run all scraping functions and store in a dictionary.
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image_scrape(browser),
        "hemispheres": hemispheres_scrape(browser),
        "weather": twitter_weather_scrape(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now()
    }

    # Stop webdriver and return data
    browser.quit()
    return data

if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())
