import requests, zipfile, os
import json, sqlite3
import json

#Reading the Destiny API Manifest in Python. [How I Did It, Anyway]

weapon_types = ['Rocket Launcher', 'Scout Rifle', 'Fusion Rifle', 'Sniper Rifle',
              'Shotgun', 'Machine Gun', 'Pulse Rifle', 'Auto Rifle', 'Hand Cannon', 'Sidearm']

#dictionary that tells where to get the hashes for each table
#FULL DICTIONARY
hash_dict = {
            'DestinyClassDefinition': 'classHash',
            'DestinyGenderDefinition': 'genderHash',
            'DestinyInventoryBucketDefinition': 'bucketHash',
            'DestinyInventoryItemDefinition': 'itemHash',
            'DestinyProgressionDefinition': 'progressionHash',
            'DestinyRaceDefinition': 'raceHash',
            'DestinyHistoricalStatsDefinition': 'statId',
            'DestinyStatDefinition': 'statHash',
            'DestinySandboxPerkDefinition': 'perkHash',
            'DestinyStatGroupDefinition': 'statGroupHash'
            }

def get_manifest():
    manifest_url = 'http://www.bungie.net/Platform/Destiny2/Manifest/'
    #get the manifest location from the json
    headers = {'x-api-key': '2589d3e06e184c02877226094b567dc5' }
    r = requests.get(manifest_url, headers=headers)
    manifest = r.json()
    mani_url = 'http://www.bungie.net'+manifest['Response']['mobileWorldContentPaths']['en']
    #Download the file, write it to MANZIP
    r = requests.get(mani_url)
    with open("MANZIP", "wb") as zip:
        zip.write(r.content)
    print "Download Complete!"
 
    #Extract the file contents, and rename the extracted file
    # to 'Manifest.content'
    with zipfile.ZipFile('MANZIP') as zip:
        name = zip.namelist()
        zip.extractall()
    os.rename(name[0], 'Manifest.content')
    print 'Unzipped!'

def build_dict(hash_dict):
    #connect to the manifest
    con = sqlite3.connect('Manifest.content')
    print 'Connected'
    #create a cursor object
    cur = con.cursor()
 
    all_data = {}
    #cur.execute("SELECT name from sqlite_master WHERE type='table'")
    #for every table name in the dictionary
    for table_name in hash_dict.keys():
        #get a list of all the jsons from the table
        cur.execute('SELECT json from '+table_name)
        print 'Generating '+table_name+' dictionary....'
 
        #this returns a list of tuples: the first item in each tuple is our json
        items = cur.fetchall()
 
        #create a list of jsons
        item_jsons = [json.loads(item[0]) for item in items]
 
        #create a dictionary with the hashes as keys
        #and the jsons as values
        item_dict = {}
        hash = hash_dict[table_name]
        print 'hash ' + hash
        # for item in item_jsons:
        #     item_dict[item[hash]] = item
        i = 1
        for item in item_jsons:
            i += 1
            name = i
            displayname = ''
            # write it anyway
            if ('itemTypeAndTierDisplayName' in item):
                name = item['itemTypeAndTierDisplayName']
            if ('displayProperties' in item and 'screenshot' in item):
                displayname = item['displayProperties']['name']
                file = open('screenshots.txt', 'a')
                file.write(name + ' ' + displayname + ' : https://bungie.net' + item['screenshot'] + '\n\r')
            # skip emotes, emblems and subclasses
            if not type(name) == int and 'Emote' not in name and 'Emblem' not in name and 'Subclass' not in name:
                print 'Adding ' + displayname
                with open('items.json', 'a+') as json_file:
                    json.dump(item, json_file);
 

    print 'Dictionary Generated!'
    return all_data

try:
   os.remove('MANZIP')
except OSError:
   pass

try:
   os.remove('Manifest.content')
except OSError:
   pass

get_manifest()
build_dict(hash_dict)
print 'Done!'