#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ftplib import FTP
from StringIO import StringIO
import zipfile
from parser_libxml import ZakupkiXMLParser
from lxml import etree
from helper import DBConnector
import psycopg2



def parse_file_id(file_id,filename):
    def get_zip_data(filename,callback):
        ftp = FTP("ftp.zakupki.gov.ru", "free", "free")
        file = ftp.retrbinary("RETR " +filename, lambda data: callback(data))
        return file
        
    zipdata = StringIO()
    get_zip_data(filename,zipdata.write)
    try:
        myzipfile = zipfile.ZipFile(zipdata)
    except:
        'Not zip file:'+filename
        return
    for name in myzipfile.namelist():
        content=myzipfile.open(name)
        tree = etree.parse(content)
        root = tree.xpath(".")
        elements=root[0].xpath("./*")
        parser=ZakupkiXMLParser()
        parser.file_id=str(file_id)
        for i in elements:
            parser.handle_element('',i)
            print '--Start--',i
           # print 'BEGIN;'
            parser.generate_insert_statements(parser.values)
           # print 'commit;'
            print '--End--',i
        parser.save_uids()
        parser.values=dict()

def main():

    db = psycopg2.connect(
    host = 'localhost',
    database = 'zakupki',
    user = 'zakupki',
    password = 'zakupki'
    )
    curr=db.cursor()
    #curr.execute("SELECT id,path FROM files_list where inserted=false")
    while  True :
        curr.execute("SELECT id,path FROM files_list where inserted=false order by id;")
        (id,path) = curr.fetchone()
	print "--Try get file" , id , path
        parse_file_id(id,path)
	curr.execute("update files_list set inserted=true where id=%s;commit;",(id,))

    

if __name__ == "__main__":
    main()


