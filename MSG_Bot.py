######################
## IMPORT LIBRARIES ##
######################
import requests
import feedparser

from time import sleep
from datetime import timedelta, datetime
from dateutil import parser


######################
## IMPORT VARIABLES ##
######################
from Non_Public_Info import Bot_Auth_Token, Bot_Channel_ChatID  # Get Info from non public .PY-file to connect to Bot


###################
## RSS FEED URLS ##
###################
URLs = ["https://www.mpg.de/feeds/jobs.rss", # Max-Planck Institute (< 4 weeks Feed provided!)
        "https://kidoktorand.varbi.com/en/what:rssfeed",    # Karolinska Institute
        "https://uu.varbi.com/what:rssfeed/",   # Uppsala University
        "https://portal.mytum.de/jobs/wissenschaftler/asRss"]  # Technical University of Munich


##########
## TAGS ##
##########
tags_diseases = []
tags_techniques = []
tags_other = ["Bioinformatics", "Pharmacometrics"]


###################################
## BOT DATA FOR SENDING MESSAGES ##
###################################

def Send_To_Channel(Message):

    bot_token = Bot_Auth_Token  # Hidden Token; Replace with own
    bot_chatID = Bot_Channel_ChatID  # Hidden Chat-ID; Replace with own

    send_text = 'https://api.telegram.org/bot' + bot_token + \
                '/sendMessage?chat_id=' + bot_chatID + \
                '&text=' + Message

    response = requests.get(send_text)

    return response.json()  # Get response Info


################################################
## IMPORT RSS DATA AND CHECK FOR NEW POSTINGS ##
################################################

# List of relevant strings in title to check for
titles = ["Doktorand", "Doctoral",
          "Doktorand*innen", "DoktorandInnen", "Doktorand*in", "Doktorand/in",
          "PhD", "PHD"," Ph.D", "Ph.D.", "(PhD)", "PhD-Student*"]


def main(URL, Limit_Hours):  # Get RSS data from URL List

    rss_data = feedparser.parse(URL)  # Get RSS Feed Data

    for entry in rss_data.entries:  # Check all available RSS Information

        parsed_title = entry.title.split()  # Split Title to extract Position

        if any(elem in titles for elem in parsed_title): # Check for PhD/Doctoral Keywords in Title

            parsed_date = parser.parse(entry.published).replace(tzinfo=None)  # Get publish date

            published_recently = datetime.now() - parsed_date < timedelta(hours=Limit_Hours)  # Check for recently

            if published_recently:
                date_published = entry.published[:len(entry.published) - 5] + "(GMT+2)"  # Replace +0200 by GMT+2

                # Combine Title, Date, Link
                msg = entry.title + "\n" \
                      + entry.links[0].href + "\n" \
                      + "Published: " + date_published

                print(msg, "\n")  # Output Title + Date to Console

                #################################
                ## UNCOMMENT HERE TO BROADCAST ##
                #################################

                # Send_To_Channel(msg)  # Output Title + Date to Telegram Channel as 1st Message

                # sleep(4)  # Timer to avoid 30 msg/min Limit


###############################################################
## RUN SEARCH FOR LIST OF URLS AND SPECIFIED UPDATE INTERVAL ##
###############################################################
Update_Interval_hours = 1  # 168 = 1 Week; 680 1 Month
Update_Interval_seconds = Update_Interval_hours * 60 * 60  # Convert to Seconds for Sleep Function

if __name__ == "__main__":
    while (True):
        for URL in URLs:    # Loop all provided URLs
            main(URL, Update_Interval_hours)

        for i in range(Update_Interval_seconds, 0, -5):
            sleep(5) # Don't Spam Console (too much)
            print("Remaining Seconds until next Check: ", i)  # Show Countdown until next Check