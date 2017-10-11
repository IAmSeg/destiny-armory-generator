# destiny-armory-generator
Python script to generate a firebase database of the Destiny armory from the Bungie API.

### Setup
You'll need an API key from bungie to use this. [Go here to setup your Bungie developer account and get an API key.](https://bungie-net.github.io/multi/index.html)

After you have an API key, create a file called `apiKey.py` that contains the following: 

```python
apiKey = 'YOUR_API_KEY_HERE'
```

You'll then need to setup a Firebase database to house your armory. [Go here for Firebase setup.](https://firebase.google.com/docs/web/setup?authuser=0). After that create a file called `firebaseConfig.py`
that contains 

```python
firebaseUrl = 'URL_TO_YOUR_FIREBASE_DB_HERE'
```

Then simply run `python manifest.py` and watch your db fill up.
