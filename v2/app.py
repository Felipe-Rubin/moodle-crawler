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
moodle_login_url = "https://moodle.pucrs.br/login/index.php"
moodle_login_redirect_page = "https://moodle.pucrs.br/my/"

#https://stackoverflow.com/questions/9012008/
#pythons-re-return-true-if-regex-contains-in-the-string
def regexp_match(exp,text):
	# p = re.search(exp,text)
	prog = re.compile(exp)
	result = prog.match(text)
	return result is not None

# Teacher Information
class Teacher:
	def __init__(self,name,link=''):
		self.name = name
		self.link = link
	def __str__(self):
		return self.name
	def __repr__(self):
		return "Teacher()"

# window.open('https://moodle.pucrs.br/mod/resource/view.php?id=1285167&redirect=1'); return false;
# class Topic

# Course Information
class Course:
	def __init__(self,name,summary='',teachers=[],link=''):
		
		self.summary = summary
		self.teachers = teachers # List of Teachers
		self.link = link
		self.name = name
		if regexp_match('\\w\\w\\w\\w\\w\\-\\d\\d',str(self.name)):
			self.type = 'special'
		else:
			self.type = 'common'

	def __str__(self):
		mystr =  'Course: '+str(self.name) + '\n'
		mystr =  'Type: '+self.type + '\n'
		mystr += 'Summary: '+str(self.summary)+'\n'
		mystr += 'Teachers: '
		for t in self.teachers:
			mystr+=str(t.name)+' '
		return mystr



# https://10minutemail.com/10MinuteMail/index.html


# Peek link to see if there's anything interesting
def peek_link(br,link):
	return 0
# Returns List of Courses
def find_courses(br):
	br.open(moodle_login_redirect_page)

	soup = br.get_current_page().find(role='main')
	soup = soup.findAll("div",{"class":{"coursebox"}})
	
	courses = []
	for course in soup:
		
		info = course.find('div',{'class':{'info'}})
		name = info.h3.a
		teachers = info.ul

		summary = course.find('div',{'class':{'summary'}}).string
		link = name['href']
		name = name.string

		cnode = Course(name=name,summary=summary,link=link) # Course Node
		# Add teachers
		for teacher in info.ul.findAll('li'):
			tnode = Teacher(teacher.a.string,link=teacher.a['href'])
			cnode.teachers.append(tnode)
		courses.append(cnode)
	return courses	


# Log in to moodle. br is the browser created with create_moodle_browser
# the browser's cookie is expected to be empty
def login(username,password,br):
	br.open(moodle_login_url) # Open login url
	form = br.select_form(selector='form', nr=0) # Select the login form (first one)
	form.set_input({'username': username, 'password': password}) # Set input fields
	br.submit_selected() # Submit the form
	
	# Check if the browser was redirected to /my, if so successful login.
	if not br.get_url() == moodle_login_redirect_page:
		print('Username and/or password invalid')
		exit(0)
	else:
		print('Logged in')
	# br.get_cookiejar() # Returns cookie jar with login cookie
	# br.close()
	return br

# Create a browser for moodle with a cookie jar
def create_moodle_browser():
	br = mechanicalsoup.StatefulBrowser(soup_config={'features': 'lxml'},user_agent='Chrome')
	cj = cookielib.LWPCookieJar() # Similar to v1, use same cookie jar
	br.set_cookiejar(cj) # Set cookie jar
	return br;


# Creates a directory
def mkdir_folder(path):
	if not os.path.exists(path):
		os.makedirs(path)
	return 0

# Writes to a file
def write_file(path,data):
	f = open(path,"w+")
	f.write(data)
	f.close()

#activity resource modtype_resource 
#activity label modtype_label 
#module-1413106
# Download a course content to the specific path
# Text as markdown
# class Activity:
# 	def __init__(self,atype,links=[],text):
# 		self.atype = atype
# 		self.links = links
# 		self.text = text
# 	def __str__(self):
# 		return 'Not Implemented Yet'





class ActivityParser:
	def __init__(self):
		types = ['activity label modtype_label ',
		'activity resource modtype_resource ',
		'activity label modtype_label ',
		'activity url modtype_url ',
		'activity page modtype_page ',
		'activity assign modtype_assign ',
		]
	# Converts HTML to Github Markdown
	def html2md(self,text=[]):
		outmd = ''
		# for t in text:
		# 	if t.name == 'h1':
		# 		outmd += t.string+'#'
		# 	elif t.name == 'h2':
		# 		outmd += t.string+'##'
		# 	elif t.name == 'h3':
		# 		outmd += t.string+'###'
		# 	elif t.name == 'h4':
		# 		outmd += t.string+'####'
		# 	elif t.name == 'h5':
		# 		outmd += t.string+'#####'
		# 	elif t.name == 'h6':
		# 		outmd += t.string+'######'
		# 	elif t.name == 'p':
		return ''

	def download_activity(self,activity):
		return 0		


class Resource:
	def __init__(self,name,link):
		self.name = name
		self.link = link
	def __str__(self):
		return str(self.name) + ' '+str(self.link)
# Parser responsible for parsing a section content
class SectionParser:
	# def __init__(self):
		# return 0

	def find_name(self,section):
		name = ''
		# print('Section Name',section['aria-label'])
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
			return section.find('object',id='resourceobject')['data']

			
	def find_urls(self,section):
		#activity url modtype_url 
		# instancename
		urls = []
		return 0

	def __str__(self):
		return 'NOREPRESENTATION'


def parse_content_sections(course_content):
	return course_content.findAll('li', id=re.compile('^section-'))

def download_course_content(path,course_content,br):
	# Get each content
	# course_topics = course_content.ul
	# for topic in course_topics:
		# print(topic['id'])
	sections = parse_content_sections(course_content)
	print('##Sections##')
	# print(sects)
	sc = SectionParser()
	current_url = br.get_url()
	for section in sections:
		print("##NAME##")
		print(sc.find_name(section))
		print("##SUMMARY##")
		print(sc.find_summary(section))
		print("##RESOURCES##")
		for res in sc.find_resources(section):
			print('Finding Actual Resource for link: ',res.link)
			br.open(res.link)
			if br.get_url() != res.link:
				res.link = br.get_url()
			else:
				res.link = sc.find_actual_resource(br.get_current_page())	
			print('Resource: ',res)
		print("#############")
		# sc.find_files()
	print('############')

	return 0
# Downloads a course
# rootdir is the output root directory
def download_course(br,course,rootdir):
	br.open(course.link)
	soup = br.get_current_page().find(role='main')
	content = soup.find('div',{'class':{'course-content'}})
	# Check if a professor uses navbar (separates pages)
	manycontent = content.find('div',{'class':{'single-section onetopic'}})
	if manycontent is not None:
		# Must iterate each subpage
		pass
	else:
		# There's only a single page
		download_course_content(rootdir+'/'+str(course.name),content,br)

	# print(course_content)
	return 0

# Main program
def main(username,password):#moodle_username,moodle_password):
	br = create_moodle_browser()
	login(username,password,br) # Log in to PUCRS Moodle 
	courses = find_courses(br) # Change Files
	print('Courses Found:')
	i = 0
	outdir = './output'
	mkdir_folder(outdir)
	for i in range(0,len(courses)):
		print(i,': ',courses[i].name)
		download_course(br,courses[i],outdir)
		# exit(0)
	return 0


main(sys.argv[1],sys.argv[2])













































