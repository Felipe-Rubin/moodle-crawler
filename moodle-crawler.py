# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import mechanize #install
from bs4 import Tag, NavigableString, BeautifulSoup #install
import urllib2 #install
import cookielib #install
import os, errno 
import re #install
import pdfcrowd #install




moodle_login_url = "https://moodle.pucrs.br/login/index.php"
moodle_login_redirect_page = "https://moodle.pucrs.br/my/"

# If you want to save 'prints' from moodle do this:
#1) Create a free account https://pdfcrowd.com
#2) Initiate a trial(no information is required) of API v2 trial activated
#3) Get your a API key
#4) Change pdf_ variables below
save_pdf_enabled = 0
pdf_api_username = ''
pdf_api_token = ''



if save_pdf_enabled == 1:
	try:
		client = pdfcrowd.HtmlToPdfClient(pdf_api_username, pdf_api_token)
	except:
		print 'PDF API not working'
		raise

#https://stackoverflow.com/questions/20039643/how-to-scrape-a-website-that-requires-login-first-with-python
# wget --quiet --save-cookies cookiejar --keep-session-cookies --post-data "action=login&login_nick=USERNAME&login_pwd=PASSWORD" -O outfile.htm http://domain.com/index.php
def save_pdf(html_string,filename):
	if save_pdf_enabled == 0:
		return
	try:
		client.convertStringToFile(str(html_string),filename)
	except pdfcrowd.Error as why:
		# report the error
		sys.stderr.write('Pdfcrowd Error: {}\n'.format(why))
		raise


def init(moodle_username,moodle_password):
	# cj = cookielib.CookieJar()
	br = mechanize.Browser()
	cj = cookielib.LWPCookieJar()
	br.set_cookiejar(cj)
	#Browser Options
	br.set_handle_equiv(True)
	# br.set_handle_gzip(True)
	br.set_handle_redirect(True)
	br.set_handle_referer(True)
	br.set_handle_robots(False)
	br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

	br.addheaders = [('User-agent', 'Chrome')]

	#Open PUCRS Moodle
	br.open(moodle_login_url)
	br.select_form(nr=0)
	br['username'] = moodle_username
	br['password'] = moodle_password
	br.submit()

	if not br.geturl() == moodle_login_redirect_page:
		print 'Username and/or password invalid'
		return 0
	else:
		print 'Logged in'
	# Logged in
	
	#Avoid Redirect, easier to parse
	# br.set_handle_refresh(False)
	# if save_pdf_enabled == 1:
	# 	try:
	# 		client = pdfcrowd.HtmlToPdfClient(pdf_api_username, pdf_api_token)
	# 	except:
	# 		print 'PDF API not working'
	# 		return 0

	br.select_form(nr=0)
	session_key = br['sesskey']
	print  'Session Key is %s',session_key
	soup = BeautifulSoup(br.response().read(),'lxml')
	# print "\n\n\n\n"
	if not os.path.exists('./output'):
		os.makedirs('./output')
	soup.findAll('script')[0].extract()
	save_pdf(soup,'./output/my.pdf')

	soup = soup.find(role='main')
	soup = soup.findAll("div",{"class":{"coursebox"}})

	for course in soup:
		# course_name = course.find("h3",{"class":{"name"}})
		course_info = course.find('div',{'class':{'info'}})
		course_summary = course.find('div',{'class':{'summary'}})
		course_name = course_info.h3.a
		course_teachers = course_info.ul
		course_link = course_name['href']
		course_title = course_name.string
		
		
		# print 'Curso: ',course_title
		# print 'Link: ',course_link
		course_data = "Curso: "+course_title+"\n"+"Link: "+course_link+"\n"
		for teacher in course_teachers.findAll('li'):
			course_data=course_data+'Professor: '+teacher.a.string+' [link: '+teacher.a['href']+"]\n"
			# print 'Professor: ',teacher.a.string,'[link: '+teacher.a['href']
		# print 'Sumario: ',course_summary.string
		try:
			course_data=course_data+'Sumario: '+course_summary.string+"\n"
		except:
			pass
		#Access this course		
		br.open(course_link)
		soup_course = BeautifulSoup(br.response().read(),'lxml')
		soup_course.findAll('script')[0].extract()
		course_content = soup_course.find('div',{'class':{'course-content'}})
		# course_topics = course_content.find('ul',{'class':{'topics'}}).findAll('li')
		course_topics = course_content.ul
		
		course_dir = "./"+'output/'+course_title;
		directory = os.path.dirname(course_dir)
		# Create course folder if it doesn't exist
		print 'Get ',directory

		if not os.path.exists(directory):
			os.makedirs(directory)   
		f = open(directory+"/"+"info.txt","w+")
		f.write(course_data)
		f.close()
		save_pdf(soup_course,"./"+'output/'+str(course_title)+'.pdf')
		no_name_counter = 0
		for ct in course_topics:
			# print "\n{"
			try:
				ct_topic = ct['aria-label']
			except:
				ct_topic = 'no_name_course_'+str(no_name_counter)
				no_name_counter = no_name_counter + 1

			ct_directory = directory+'/'+ct_topic
			if not os.path.exists(ct_directory):
				os.makedirs(ct_directory)

			try:
				course_topic_content = ct.find('div',{'class':{'content'}})
				course_topic_summary = ct.find('div',{'class':{'summary'}})
			except:
				continue
			# Still need to parse this
			urlPack = ''
			pagePack = ''
			try:
				for lk in course_topic_summary.findAll('a'):
					lk_link = lk['href']
					lk_filename = re.sub(r'.*/','',lk_link)
					if '.htm' not in lk_link and '.html' not in lk_filename and lk_filename != '':
						try:
							# if not os.path.exists(ct_directory+'/'+lk_filename):
							br.retrieve(lk_link,ct_directory+'/'+lk_filename)
						except:
							urlPack = urlPack + str(lk_link)+'\n'
					else:
						urlPack = urlPack + str(lk_link)+'\n'
			except:
				continue

			try:
				activities = course_topic_content.ul
			except:
				continue

			try:
				for activity in activities:
					#['activity', 'label', 'modtype_label', '']
					#['activity', 'forum', 'modtype_forum', '']
					#['activity', 'assign', 'modtype_assign', '']
					#['activity', 'url', 'modtype_url', '']
					#['activity', 'page', 'modtype_page', '']
						if activity.get('class') == ['activity', 'resource', 'modtype_resource', '']:
							activity_instance = activity.find('div',{'class':{'activityinstance'}})
							activity_link = activity_instance.a['onclick']
							activity_link = re.sub(r'((window\.open\(\'))|(&amp)(.)*|((&redirect)(.)*)','',activity_link)
							# print 'RedirectLink: ',activity_link
							
							
							br.open(activity_link)
							soup_redirect = BeautifulSoup(br.response().read(),'lxml')
							true_activity_link = soup_redirect.find('div',{'class':{'resourceworkaround'}}).a['href']
							true_activity_filename = re.sub(r'.*/','',true_activity_link)
							# print 'TrueLink: ',true_activity_filename,":",true_activity_link

							br.retrieve(true_activity_link,ct_directory+'/'+true_activity_filename)
						elif activity.get('class') == ['activity', 'url', 'modtype_url', '']:
							activity_instance = activity.find('div',{'class':{'activityinstance'}})
							activity_name = activity_instance.find('span',{'class':{'instancename'}}).text
							# print 'UrlActivityName: ',activity_name
							activity_link = activity_instance.a['href']
							br.open(activity_link)
							true_activity_link = ''
							try:
								soup_redirect = BeautifulSoup(br.response().read(),'lxml')
								true_activity_link = soup_redirect.find('div',{'class':{'urlworkaround'}}).a['href']
							except: #Happens when there's a redirect
								true_activity_link = br.geturl()
							urlPack = urlPack + str(activity_name)+': ['+str(true_activity_link)+']'+'\n'
						elif activity.get('class') == ['activity', 'page', 'modtype_page', '']:
							activity_instance = activity.find('div',{'class':{'activityinstance'}})
							activity_link = activity_instance.a['onclick']
							activity_link = re.sub(r'((window\.open\(\'))|(&amp)(.)*|((&redirect)(.)*)','',activity_link)
							activity_name = activity_instance.find('span',{'class':{'instancename'}}).text
							br.open(activity_link)
							soup_redirect = BeautifulSoup(br.response().read(),'lxml')
							soup_redirect.findAll('script')[0].extract()
							save_pdf(soup_redirect,ct_directory+'/'+true_activity_filename+'.pdf')
							# options = {"cookie": cj}
							# config = pdfkit.configuration(wkhtmltopdf='./wkhtmltopdf')
							# pdfkit.from_url(activity_link, "./out.pdf", options=options, configuration=config)
						else:
							# print ''
							pass
			except:
				pass
	print 'Done!'
	print 'Moodle downloaded to ./output/'
init(sys.argv[1],sys.argv[2])







