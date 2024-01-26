

import requests

import sqlite3
import base64


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


conn = sqlite3.connect('v8_debug.db')
cursor = conn.cursor()

# Create a table if it does not exist
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


pageToken = "CjpsaW51eC1kZWJ1Zy9kOC1hcm0tYXNhbi1saW51eC1kZWJ1Zy12OC1jb21wb25lbnQtMzQxNjUuemlw"

# GET PAGET TOKEN FROM DB
try:
    cursor.execute('SELECT nextPageToken FROM files ORDER BY id DESC LIMIT 1')
    pageToken = cursor.fetchone()[0]
except:
    pass

print("pageToken: " + pageToken)

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


conn.close()

