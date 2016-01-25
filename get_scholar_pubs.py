#! /usr/bin/env python

import argparse
import urllib
import urllib2
from bs4 import BeautifulSoup
from docx import Document

def main():

    parser = argparse.ArgumentParser(description=\
        'Parse and format publication list from your Google Scholar profile.')
    req = parser.add_argument_group('required arguments')
    req.add_argument('-u', '--user', required=True,
        type=str, help='Your Google Scholar user string. You can find this \
        in the URL of your Google Scholar profile between the "user=" and \
        the "&" character. Mine is 12 letters long with lowercase and \
        uppercase letters.')
    req.add_argument('-o', '--output_fp', required=True,
        help='The output filepath for the formatted publication list. \
        Only outputs .docx format for now.')
    # parser.add_argument('-f', '--output_format',
    #     help='The output format.')

    args = parser.parse_args()

    output_fp = args.output_fp

    # full profile url. gets all records on one page
    data = {}
    data['hl'] = 'en'
    data['user'] = args.user
    data['start'] = 0
    data['pagesize'] = 1000
    url_values = urllib.urlencode(data)
    my_url = "https://scholar.google.com/citations"
    full_url = my_url + '?' + url_values

    # set user agent -- hopefully will help Google to allow automated access
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64; rv:27.0) Gecko/20100101 Firefox/27.0'
    headers = { 'User-Agent' : user_agent }
    # get page
    req = urllib2.Request(full_url, {}, headers)
    response = urllib2.urlopen(req)
    html = response.read()
    soup = BeautifulSoup(html, 'html.parser')

    pubs_data = {}
    pubs_year = {}

    pubs = soup.findAll("a", { "class" : "gsc_a_at" })
    for i, pub in enumerate(pubs):
        base = "https://scholar.google.com"
        cit_url = base + pub.get('href')
        cit_data = get_citation_data(cit_url)
        if 'Journal' in cit_data:
            pubs_data[i] = cit_data
            pubs_year[i] = int(cit_data['Year'])

    doc = Document()
    for i, pub_no in enumerate(sorted(pubs_year, key=pubs_year.get, reverse=True)):
        pub_no_print = str(i + 1) + "."
        try:
            vol = ", " + pubs_data[pub_no]['Volume']
        except KeyError:
            vol = ""
        try:
            issue = ":" + pubs_data[pub_no]['Issue']
        except KeyError:
            issue = ""
        authors = format_authors(pubs_data[pub_no]['Authors'])
        outLine = "%s. %s. %s. %s%s%s.\n" %(
            authors,
            pubs_data[pub_no]['Year'],
            pubs_data[pub_no]['Title'],
            pubs_data[pub_no]['Journal'],
            vol,
            issue)
        print outLine
        doc.add_paragraph(outLine, style='ListNumber')
    doc.save(output_fp)


def get_citation_data(url):
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64; rv:27.0) Gecko/20100101 Firefox/27.0'
    headers = { 'User-Agent' : user_agent }
    req = urllib2.Request(url, {}, headers)
    response = urllib2.urlopen(req)
    html = response.read()
    cit_soup = BeautifulSoup(html, 'html.parser')
    data = {}
    # get title
    title = cit_soup.find("a", { "class" : "gsc_title_link" })
    data['Title'] = title.text
    # get data
    fields = cit_soup.findAll("div", { "class" : "gsc_field" })
    values = cit_soup.findAll("div", { "class" : "gsc_value" })
    for field, value in zip(fields, values):
        data[field.text] = value.text
        if field.text == 'Publication date':
            data['Year'] = value.text.split('/')[0]
    return data

def format_authors(authors):
    split_auths = authors.split(',')
    formatted_authors = []
    for auth in split_auths:
        spl_auth = auth.split(' ')
        initials = []
        for i, name in enumerate(spl_auth):
            if i == len(spl_auth) - 1:
                last = name
            else:
                try:
                    initials.append(name[0])
                except IndexError:
                    pass
        formatted_authors.append(''.join(initials) + " " + last)
    return ', '.join(formatted_authors)


if __name__ == '__main__':
    main()
