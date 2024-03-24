# Imporing necessary libraries
from bs4 import BeautifulSoup
import requests
import pandas as pd
import datetime as dt
import pycountry

#_________________________________Crating containers for df_____________________________#

# Creating a list for contain data and use it in Df
review_dates = []
reviewer_experience_dates = []
reveiwer_names = []
review_ratings = []
review_titles = []
review_descriptions = []
review_country_codes = []
review_countries =[]
review_total_counts = []
review_links = []


#_________________________________Page to scrap_____________________________#
        
# Set Trustpilot page numbers you want to scrape. Larger range will take more time
from_page = 1
to_page = 50

#_________________________________Actual Webscrapping begins here_____________________________#
        

for i in range(from_page, to_page + 1):
    response = requests.get(f"https://www.trustpilot.com/review/company_name.com?page={i}") # place you website name here. Don't remove "?page="     
    web_page = response.text
    soup = BeautifulSoup(web_page, "html.parser")

    # Looping through each review
    for review in soup.find_all(class_="styles_cardWrapper__LcCPA styles_show__HUXRb styles_reviewCard__9HxJJ"):
        
        # Review dates
        review_date_original = review.find("time")["datetime"]
        review_date_iso = review_date_original[:-1] # Remove timezone information
        review_parsed_datetime = dt.datetime.fromisoformat(review_date_iso) # Parse datetime string into a datetime object
        review_formatted_datetime = review_parsed_datetime.strftime("%Y-%m-%d %H:%M:%S") # Format the datetime object as desired
        review_dates.append(review_formatted_datetime) # Append formatted datetime to the list
        
        # Reviewer Date of Experience (Issue)
        reviewer_experience_date = review.find(class_="typography_body-m__xgxZ_ typography_appearance-default__AAY17")
        reviewer_experience_date_string = reviewer_experience_date.getText()
        reviewer_experience_date_extract = reviewer_experience_date_string.split(": ")[1] # splitting date from string
        reviewer_experience_date_formating = dt.datetime.strptime(reviewer_experience_date_extract, "%B %d, %Y").date() # formatting the date
        reviewer_experience_dates.append(reviewer_experience_date_formating)


        # Reviwer Names
        reveiwer_name = review.find(class_="typography_heading-xxs__QKBS8 typography_appearance-default__AAY17")
        reveiwer_names.append(reveiwer_name.getText())

        # Review ratings
        review_rating = review.find(class_ = "star-rating_starRating__4rrcf star-rating_medium__iN6Ty").findChild()
        review_ratings.append(review_rating["alt"])


        # Review Titles
        review_title = review.find(class_="typography_heading-s__f7029 typography_appearance-default__AAY17")
        if review_title == None: # if there are no title, then the value will be blank. 
            review_titles.append("")
        else:
            review_titles.append(review_title.getText()) 


        # Review Descriptions
        review_description = review.find(class_ = "typography_body-l__KUYFJ typography_appearance-default__AAY17 typography_color-black__5LYEn")
        if review_description == None: ## if there are no description, then the value will be blank. 
            review_descriptions.append("")
        else:
            review_descriptions.append(review_description.getText())    

        # Reviwer Two Letter Country Code
        review_country_code_element = review.find(class_="typography_body-m__xgxZ_ typography_appearance-subtle__8_H2l styles_detailsIcon__Fo_ua")
        review_country_code = review_country_code_element.getText() if review_country_code_element else "Not found"
        review_country_codes.append(review_country_code)


        # Reviewer Country Name Identifying by using pycountry
        try:
            review_country = pycountry.countries.get(alpha_2=review_country_code).name
        except AttributeError:
            review_country = "Unknown"  # Handle the case where the country code is invalid or not found

        # Append the country name to the list
        review_countries.append(review_country)

        # Review total Review Counts
        review_total_count = review.find(class_ = "typography_body-m__xgxZ_ typography_appearance-subtle__8_H2l").getText() 
        review_total_counts.append(review_total_count)


        # Review Links
        review_link = review.find(class_="styles_reviewContent__0Q2Tg").find('a')["href"] #finding link from <a> tag
        review_link_adjusting = "https://www.trustpilot.com/" + review_link #joining default website with review link
        review_links.append(review_link_adjusting)


#_________________________________Adjusting columns data_____________________________#

# Only keeping the number from string
review_total_counts_int = [
    # If it's an integer, use it directly
    x if isinstance(x, int) 
    # If it's a list, take the first item, split by space, and convert the first part to int
    else int(x[0].split()[0]) if isinstance(x, list) 
    # If it's a string, split by space, and convert the first part to int
    else int(x.split()[0]) 
    for x in review_total_counts
]

# Only keeping the numbers from string
review_ratings_int = [int(x.split()[1]) if isinstance(x, str) else x for x in review_ratings]



#_________________________________Prepairing the DF_____________________________#
# Create final dataframe from lists
trustpilot_reviews_df = pd.DataFrame(list(zip(review_dates, reviewer_experience_dates, reveiwer_names, review_ratings_int, review_titles, review_descriptions, review_country_codes, review_countries, review_total_counts_int, review_links)),
                columns =['review_dates','reviewer_experience_dates', 'reveiwer_names', 'review_ratings', 'review_titles', 'review_descriptions', 'review_country_codes', 'review_countries', 'review_total_counts', 'review_links'])


#_________________________________Download Data as CSV file_____________________________#
## if you want to download a csv file
trustpilot_reviews_df.to_csv(r'G:\Python\trustpilot.csv', index=False)















