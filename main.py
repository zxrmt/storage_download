

import requests

import sqlite3
import base64
import sys, os
import re

headers = {
    'authority': 'www.googleapis.com',
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-US,en;q=0.9,vi;q=0.8,pt;q=0.7',
    'origin': 'https://commondatastorage.googleapis.com',
    'referer': 'https://commondatastorage.googleapis.com/',
    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}



def create_and_init_db(name):

    print("Connect to db and create table", name)
    conn = sqlite3.connect(name)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nextPageToken TEXT,
            mediaLink TEXT,
            name TEXT,
            size TEXT,
            updated TEXT,
            cr_commit_position_number TEXT,
            cr_git_commit TEXT,
            cr_commit_position TEXT
        )
    ''')
    return cursor, conn

# List all db file in current directory
db_files = [f for f in os.listdir('.') if re.match(r'.*\.db', f)]

if len(db_files) == 0:

    pageToken = "CjpsaW51eC1kZWJ1Zy9kOC1hcm0tYXNhbi1saW51eC1kZWJ1Zy12OC1jb21wb25lbnQtMzQxNjUuemlw"

    response = requests.get(
                    f'https://www.googleapis.com/storage/v1/b/v8-asan/o?delimiter=/&prefix=linux-debug/&fields=items(kind,mediaLink,metadata,name,size,updated),kind,prefixes,nextPageToken&pageToken={pageToken}',
                    headers=headers,
                )

    res = response.json()
    if (not 'items' in res):
        print("No more items")

    name = res['items'][0]['name']
    name = "_".join(name.split("-")[:-1]).replace("/","_") + ".db"
    print(name)

    cursor, conn = create_and_init_db(name)
    while True:
        response = requests.get(
            f'https://www.googleapis.com/storage/v1/b/v8-asan/o?delimiter=/&prefix=linux-debug/&fields=items(kind,mediaLink,metadata,name,size,updated),kind,prefixes,nextPageToken&pageToken={pageToken}',
            headers=headers,
        )

        res = response.json()
        if (not 'items' in res):
            print("No more items")
            break
        

        for data in res['items']:   
            if "experimental" in data['name']:
                data_name = data['name'].replace("-experimental","")    
            else:
                data_name = data['name']
            item_name = "_".join(data_name.split("-")[:-1]).replace("/","_") + ".db"
            if item_name != name:
                print("NAME:", data['name'], "\nCreate new db", item_name)
                cursor, conn = create_and_init_db(item_name)
                name = item_name

            # Create SQLite connection and cursor
            # Insert data into the table
            cursor.execute('''
                INSERT INTO files (nextPageToken, mediaLink, name, size, updated, cr_commit_position_number, cr_git_commit, cr_commit_position)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                pageToken,
                data['mediaLink'],
                data['name'],
                data['size'],
                data['updated'],
                data['metadata']['cr-commit-position-number'],
                data['metadata']['cr-git-commit'],
                data['metadata']['cr-commit-position']
            ))

            # Commit the changes and close the connection
            conn.commit()
            print("Inserted: " + data['name'], data['updated'], data['metadata']['cr-git-commit'])
        
        pageToken = res['nextPageToken']

