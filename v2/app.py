#!/bin/python3

import argparse #install
import sys
import os
import requests #install
from bs4 import BeautifulSoup #install bs4
import mechanicalsoup #install
import re 

import http.cookiejar as cookielib
# import cookielib #install


################################ UTIL ################################
# Returns True if a regular exp matches a text, otherwise False
def regexp_match(exp,text):
	prog = re.compile(exp)
	result = prog.match(text)
	return result is not None
# types = ['activity label modtype_label ',
# 'activity resource modtype_resource ',
# 'activity label modtype_label ',
# 'activity url modtype_url ',
# 'activity page modtype_page ',
# 'activity assign modtype_assign ',
# ]
# https://10minutemail.com/10MinuteMail/index.html
class FileManager:
	def __init__(self,br):
		self.br = br # Browser
	# Creates a directory
	def mkdir_folder(self,path):
		if not os.path.exists(path):
			os.makedirs(path)
		return 0
	# Writes to a file
	def write_file(self,path,data):
		f = open(path,"w+")
		f.write(data)
		f.close()
	def download_file(self,path,url):
		# file_name = ''
		# if url.find('/'):
		# 	file_name = url.rsplit('/',1)[1]

		resp = self.br.session.get(url,allow_redirects=True)
		resp.raise_for_status()

		file_type = resp.headers['Content-Type']
		with open(path,'wb') as fr:
			fr.write(resp.content)

		# self.br.download_link(link=url, file=path)
		# return 0

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('-v','--verbosity',help='Verbose Mode',required=False,default=False)
	parser.add_argument('-u',"--username", help="Login username",required=True)
	parser.add_argument('-p',"--password", help="Login password",required=True)
	parser.add_argument('-lurl',"--loginurl", help="Moodle login url",required=False,default=moodle_login_url)
	parser.add_argument('-hurl',"--homeurl", help="Moodle home url (after login)",required=False,default=moodle_home_url)
	args = parser.parse_args()
	return args

####################################### GLOBAL DEFAULTS ######################################
moodle_home_url = 'https://moodle.pucrs.br/my/'
moodle_login_url = 'https://moodle.pucrs.br/login/index.php'
####################################### Classes ###############################################

# Teacher Information
class Teacher:
	def __init__(self,name,link=''):
		self.name = name
		self.link = link
	def __str__(self):
		return str(self.name)
# Course Information
class Course:
	def __init__(self,name,summary='',teachers=[],link='',sections=[]):
		self.summary = summary # Summary
		self.teachers = teachers # List of Teachers
		self.link = link # Link for course's page
		self.name = name # Name
		self.sections = sections
		# Check if course is a normal or not (has codicred)
		if regexp_match('\\w\\w\\w\\w\\w\\-\\d\\d',str(self.name)):
			self.type = 'special'
		else:
			self.type = 'common'
	def __str__(self):
		mystr = ''
		mystr +=  'Course: '+str(self.name) + '\n'
		mystr +=  'Type: '+self.type + '\n'
		mystr += 'Summary: '+str(self.summary)+'\n'
		mystr += 'Teachers: '
		for t in self.teachers:
			mystr+=str(t)+' '
		mystr += 'Sections: \n'
		for sec in self.sections:
			mystr+= str(sec) +'\n'
		return mystr
	def about_course(self):
		mystr = ''
		mystr +=  'Course: '+str(self.name) + '\n'
		mystr +=  'Type: '+self.type + '\n'
		mystr += 'Summary: '+str(self.summary)+'\n'
		mystr += 'Teachers: '
		for t in self.teachers:
			mystr+=str(t)+' '
		return mystr

class Section:
	def __init__(self,name='noname',summary='',activities=[],resources=[]):
		self.name = name
		self.summary = summary
		self.activities = activities
		self.resources = resources
	def __str__(self):
		mystr = ''
		mystr += 'Name: ' + str(self.name)+'\n'
		mystr += 'Summary: '+ str(self.summary)+'\n'
		mystr += 'Activities:\n'
		for act in self.activities:
			mystr += str(act)
		mystr += 'Resouces:\n'
		for res in self.resources:
			mystr += str(res)
		return mystr
#Link: Link of activity page
#reslink: Link of activity resource
class Activity:
	def __init__(self,name,link,reslink=''):
		self.name = name # Activity Name
		self.link = link # Link for activity
		self.reslink = reslink # Link for resource, may be None
	def __str__(self):
		return str(self.name) + ' '+str(self.link)+' '+str(self.reslink)
class Resource:
	def __init__(self,name,link):
		self.name = name # Resource Name
		self.link = link # Link for Resource
	def __str__(self):
		return str(self.name) + ' '+str(self.link)
################################# PARSERS ######################################################
# Parser responsible for parsing a section content
class SectionParser:
	def find_name(self,section):
		name = ''
		# First try
		name = section['aria-label'] #1st try
		if name == ' ':  # 2nd try
			name = section.find('span',{'class':{'hidden sectionname'}}).string
			if name == ' ': # 3rd try
				name = section.find('div',{'class':{'content'}})\
				.find('h3',{'class':{'sectionname'}})\
				.find('span').string
				if name is None or name == '' or name == ' ':
					name = section['id']
		return name
	def find_summary(self,section):
		# return = ct.find('div',{'class':{'summary'}})
		return section.find('div',{'class':{'content'}}).find('div',{'class':{'summary'}})
	def find_modules(self,section):
		return course_content.findAll('li', id=re.compile('^module-'))
	def find_files(self,section): #Find all the files
		print("##LINKS###")
		print(section.links())
		print("##########")
	# Finds resources such as PDFs, zip files and more
	def find_resources(self,section):
		resources = []
		modresources = section.findAll('li',{'class':{'activity resource modtype_resource'}})
		for resource in modresources:

			res =  resource.find('div',{'class':{'activityinstance'}})
			name = res.a.find('span',class_='instancename').contents[0]
			link = res.a['href']
			resources.append(Resource(name,link))
		return resources
	def find_actual_resource(self,section):
		workaround = section.find('div',{'class':{'resourceworkaround'}})
		if workaround is not None:
			return workaround.a['href']
		else:
			# section.find('object',{'id':{'resourceworkaround'}})
			resourceobject = section.find('object',id='resourceobject')
			if resourceobject is not None:
				return resourceobject['data']
			else:
				return None
	def find_activities(self,section):
		activities = []
		modactivities = section.findAll('li',{'class':{'activity page modtype_page'}})
		for activity in modactivities:
			res =  activity.find('div',{'class':{'activityinstance'}})
			name = res.a.find('span',class_='instancename').contents[0]
			link = res.a['href']
			activities.append(Activity(name,link))
		return activities
	# Parse home page, get each course information
	def find_courses(self,home_page):
		soup = home_page.findAll("div",{"class":{"coursebox"}})
		courses = []
		for course in soup:
			info = course.find('div',{'class':{'info'}})
			name = info.h3.a
			teachers = info.ul
			summary = course.find('div',{'class':{'summary'}}).string
			link = name['href']
			name = name.string
			cnode = Course(name=name,summary=summary,link=link) # Course Node
			for teacher in info.ul.findAll('li'): # Add teachers
				tnode = Teacher(teacher.a.string,link=teacher.a['href'])
				cnode.teachers.append(tnode)
			courses.append(cnode)

		return courses
	# Find and return each section of a course
	def find_sections(self,course_content,br):
		sections = []
		modsections = course_content.findAll('li', id=re.compile('^section-'))
		sp = SectionParser()
		for modsect in modsections:
			name = sp.find_name(modsect)
			summary = sp.find_summary(modsect)
			resources = sp.find_resources(modsect)
			for res in resources:
				br.open(res.link)
				if br.get_url() != res.link:
					res.link = br.get_url()
				else:
					res.link = sp.find_actual_resource(br.get_current_page())
			activities = sp.find_activities(modsect)
			for act in activities:
				br.open(act.link)
				if br.get_url() != act.link: # Must check if it won't open directly ?
					act.link = br.get_url() #There wasn't any despription, just redirect
					act.reslink = br.get_url()
				else:
					act.reslink = sp.find_actual_resource(br.get_current_page())
			sections.append(Section(name,summary,activities,resources))
		return sections		
	

# login_url: The url where you normally input username and password
# home_url: The home url of moodle after you log in 
class MoodleCrawler:

	def __init__(self,login_url,home_url):
		self.courses = []
		self.login_url = login_url
		self.home_url = home_url
		# the browser's cookie is expected to be empty
		# Create a browser for moodle with a cookie jar
		self.br = mechanicalsoup.StatefulBrowser(soup_config={'features': 'lxml'},user_agent='Chrome')
		cj = cookielib.LWPCookieJar() # Similar to v1, use same cookie jar
		self.br.set_cookiejar(cj) # Set cookie jar
		self.logged_in = False
		self.sp = SectionParser()
		self.fm = FileManager(self.br)

	# Returns True if log in was successful, False otherwise
	def login(self,username,password):
		self.br.open(self.login_url) # Open login url
		form = self.br.select_form(selector='form', nr=0) # Select the login form (first one)
		form.set_input({'username': username, 'password': password}) # Set input fields
		self.br.submit_selected() # Submit the form
		# Check if the browser was redirected to /my, if so successful login.
		if not str(self.br.get_url()) == str(self.home_url):
			self.logged_in = False
		else:
			self.logged_in = True
		return self.logged_in #Logged in
	
	# Process only the top level information about each course
	def find_courses(self):
		self.br.open(self.home_url)
		soup = self.br.get_current_page().find(role='main')
		self.courses = self.sp.find_courses(soup)
		return 0

	# Process a course deep level information
	def process_course(self,course):
		self.br.open(course.link)
		soup = self.br.get_current_page().find(role='main')
		content = soup.find('div',{'class':{'course-content'}})
		# Check if a professor uses navbar (separates pages)
		manycontent = content.find('div',{'class':{'single-section onetopic'}})
		if manycontent is not None: # Must iterate each subpage
			navbar = manycontent.find(class_='nav nav-tabs mb-3')
			# print(navitems)
			if navbar is not None: # The usual way of using tabss
				navitems = navbar.findAll(class_='nav-item')
				for ni in navitems:
					if ni.a['class'] == ['nav-link', 'disabled']: # Item not enabled
						continue
					elif ni.a['class'] == ['nav-link', 'active']: # It's already on the page
						content = manycontent.find('ul',class_='topics')
						course.sections.extend(self.sp.find_sections(content,self.br))
					else: # must access the page
						self.br.open(ni.a['href'])
						content = self.br.get_current_page().find('ul',class_='topics')
						course.sections.extend(self.sp.find_sections(content,self.br))
			else: # Unusual way, will try to parse it
				navbar = manycontent.find(class_=re.compile('^nav nav-tabs'))
				if navbar is not None:
					navitems = navbar.findAll('li')
					for ni in navitems:
						if 'class' in ni.attrs and 'active' in ni['class']:
							# It's already on the page
							content = manycontent.find('ul',class_='topics')
							course.sections.extend(self.sp.find_sections(content,self.br))
						elif 'href' in ni.a.attrs:  # must access the page
							self.br.open(ni.a['href'])
							content = self.br.get_current_page().find('ul',class_='topics')
							course.sections.extend(self.sp.find_sections(content,self.br))
						else:
							continue
		else: # There's only a single page
			course.sections = self.sp.find_sections(content,self.br)
		return 0

	def download_course(self,course,path='./output'):
		rpath = path+'/'+course.name+'/'
		self.fm.mkdir_folder(path+'/'+course.name)
		for section in course.sections:
			spath = rpath+section.name+'/'
			self.fm.mkdir_folder(spath)
			for res in section.resources:
				self.fm.download_file(spath+res.name,res.link)
			for act in section.activities:
				if act.reslink is not None:
					try:
						self.fm.download_file(spath+act.name,act.reslink)
					except:
						pass
			self.fm.write_file(spath+'about.txt',str(section))
		self.fm.write_file(rpath+'about.txt',str(course.about_course()))










####################################### APP ##################################################



def main():
	args = parse_args()
	
	mc = MoodleCrawler(args.loginurl,args.homeurl)
	if not mc.login(args.username,args.password):
		print("Could not Log in")
		exit(0)		
	else:		
		print('Login Successful')


	print('Finding Courses...')
	mc.find_courses()
	print('Found [%d] courses' % len(mc.courses))
	print('Processing Courses...')
	for course in mc.courses:
		print(course.name)
		mc.process_course(course)
		mc.download_course(course)

	print('Downloading Courses...')
	return 0


main()











































