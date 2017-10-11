import requests, zipfile, os
import json, sqlite3
import json
from apiKey import *
from firebaseUrl import *
from firebase import firebase
firebase = firebase.FirebaseApplication(firebaseUrl, None)

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

# Gets the Destiny manifest from the bungie API
# Writes the manifest to a .content file
def get_manifest():
    manifest_url = 'http://www.bungie.net/Platform/Destiny2/Manifest/'
    # get the manifest location from the json
    headers = { 'x-api-key': apiKey }
    r = requests.get(manifest_url, headers=headers)
    manifest = r.json()
    mani_url = 'http://www.bungie.net'+manifest['Response']['mobileWorldContentPaths']['en']

    # Download the file, write it to MANZIP
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

# Reads from the .content file created above and writes our items to the firebase armory
def write_to_armory(hash_dict):
    #connect to the manifest
    con = sqlite3.connect('Manifest.content')
    print 'Connected'
    #create a cursor object
    cur = con.cursor()

    all_data = {}
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
        for item in item_jsons:
           # if it contains a itemTypeAndTierDisplayName, extract it
           # the itemTypeAndTierDisplayName is like 'Common Sidearm' or 'Exotic Helmet'
           if ('itemTypeAndTierDisplayName' in item):
               name = item['itemTypeAndTierDisplayName']
               tier = name.split(' ', 1)[0]

           # get the name from the display properties
           if ('displayProperties' in item and 'screenshot' in item):
               # build our real display name by putting our extract tier and type in front of the display property name
               displayname = name + ' ' + item['displayProperties']['name']
               description = item['displayProperties']['description']
               link =  'https://bungie.net' + item['screenshot']
               # build our data object with the display name, description and a link to the image
               data = { 'name': displayname, 'description': description, 'link': link }
               # skip emotes, emblems and subclasses
               if 'Emote' not in name and 'Emblem' not in name and 'Subclass' not in name:
                   print 'Adding ' + displayname
                   # stick it in the db
                   firebase.post('armory/' + tier, data=data)



try:
    os.remove('MANZIP')
except OSError:
    pass

try:
    os.remove('Manifest.content')
except OSError:
    pass


get_manifest()
write_to_armory(hash_dict)
print 'Done!'
