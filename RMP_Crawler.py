import requests
import json
import pymongo
from bs4 import BeautifulSoup

db = pymongo.MongoClient().local.ratemyprofs
professor_list = []


class Professor:
	def __init__(self, prof):
		self.tid = prof["tid"]
		self.first_name = prof["tFname"]
		self.middle_name = prof["tMiddlename"]
		self.last_name = prof["tLname"]
		self.department = prof["tDept"]
		self.overall_rating = prof["overall_rating"]
		self.rating_class = prof["rating_class"]
		self.num_ratings = prof["tNumRatings"]
		self.tags = []
		self.difficulty = 0


# %% Scrape json view of RMP for as much data as possible
for i in range(1, 150):
	query = "http://www.ratemyprofessors.com/filter/professor/?department=&page=" + str(i) + "&filter=teacherlastname_sort_s+asc&query=*%3A*&queryoption=TEACHER&queryBy=schoolId&sid=1441"

	page = requests.get(query)
	jsonpage = json.loads(page.content)
	professors = jsonpage['professors']

	if len(professors) > 0:
		for prof in professors:
			professor_list.append(Professor(prof))
	else:
		print("Found", len(professor_list), "profs")
		# print(professor_list)
		break


# %% Crawl actual RMP pages using BS4 to obtain remaining data
for prof in professor_list:
	if prof.overall_rating != 'N/A':
		query = "http://www.ratemyprofessors.com/ShowRatings.jsp?tid=" + str(prof.tid)
    
		page = requests.get(query)
		soup = BeautifulSoup(page.content, 'html.parser')
    
		difficulty = soup.find_all("div", class_="breakdown-section difficulty")
		prof.difficulty = str(difficulty).replace(' ', '').replace('\n', '').split('<divclass="grade"title="">')[1].split('</div>')[0]
    
		tags = soup.find_all("span", class_="tag-box-choosetags")
		for tag in tags:
			prof.tags.append(str(tag).split('<span class="tag-box-choosetags"> ')[1 ].split(' <b>')[0])
    
		# if prof.first_name == 'Russell':
			# break
	else:
		prof.difficulty = 'N/A'
		prof.tags = 'N/A'
