# moodle-crawler
Download all files from your pucrs moodle account

# Requirements:
- python v2
- pip
- - beautifulsoup4
- - pdfcrowd
- - mechanize
- - urllib2
- - cookielib
- - re

# Run:
``python
  python moodle-crawler.py <moodle_username> <moodle_password> 
``

# General Information
- Check code header comment to see how to genere
## If you want to save 'prints' from moodle do this:
- Create a free account https://pdfcrowd.com
- Initiate a trial(no information is required) of API v2 trial activated
- Get your a API key
- Change pdf_ variables in the script (right after the imports)
- - save_pdf_enabled = 1
- - pdf_api_username
- - pdf_api_token
