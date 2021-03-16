import dateutil.parser as dparser
import datetime
import requests
import re
import sys


# looks up the author of a web page
def get_author(html):
    author = ""

    # finds all two-three word groups that start with capital letters
    names = re.findall(r"[A-Z][a-z]+,?\s+(?:[A-Z][a-z]*\.?\s*)?[A-Z][a-z]+", html)

    # looks for author tag in the html
    potential_authors = []
    potential_authors_idx = [m.start() for m in re.finditer('author', html)]

    for i in potential_authors_idx:
        author = html[i:i+30]
        author = re.sub("[^a-zA-Z]+", " ", author)
        potential_authors.append(author)

    # checks author tags against all found names to find actual author
    # since articles could have many names and we want the right one.
    for i in names:
        for j in potential_authors:
            if str(i).lower() in str(j).lower():
                first_last = i.split(" ")
                last_first = ""
                last_first += first_last[1] + ", " + first_last[0] + "."
                return last_first
    return ""


# just adds the current date to the end of the citation
def get_access_date(months):
    today = datetime.datetime.now()
    return "Accessed " + str(today.day) + " " + months[today.month-1] + ", " + str(today.year) + "."


# looks up the title tag in the html to get the title of the article
def get_title(html):
    title_start_index = html.index("<title>")
    title_end_index = html.index("</title>")

    return '"' + html[title_start_index+7:title_end_index] + '."'


# looks up dates in form of xxxx-xx-xx to hopefully return the correct publish date
def get_date(html, months):
    potential_date_idx = [m.start() for m in re.finditer('date', html)]
    for i in potential_date_idx:
        potential_date = html[i:i+85]
        match = re.search('19|20\d{2}-\d{2}-\d{2}',potential_date)
        if match:
            date = match.group(0)
            ymd = date.split("-")
            date = ""
            date += ymd[2] + " " + months[int(ymd[1])-1] + ", " + ymd[0] + "."
            return date
        return ""


# takes a url and creates a citation out of it
def cite(url):
    html = requests.get(url).text
    months = ["January",
              "February",
              "March",
              "April",
              "May",
              "June",
              "July",
              "August",
              "September",
              "October",
              "November",
              "December"]

    citation = ""

    citation += get_author(html) + " " + get_title(html) + " " + get_date(html, months) + " " + url + " " + get_access_date(months)
    return citation



citations = []

with open("urls.txt") as f:
    lines = (line.rstrip() for line in f) # All lines including the blank ones
    lines = (line for line in lines if line) # Non-blank lines
    for line in lines:
        try:
            citations.append(cite(line))

        except:
            print("didn't work - ",line,"\n")
            continue

citations = sorted(citations)

for i in citations:
    print(i,"\n")
