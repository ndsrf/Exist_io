# Exist.io

Integrations with https://exist.io/ for self quantification. I highly recommend reading their API documentation (https://developer.exist.io/), it is very good.

## Integrations in this repo

Please let me apologise first as these are all quick and dirty implementations, I am far from being an experienced developer in Python!

### Fintonic (https://www.fintonic.com/)

Fintonic allows you to have all your bank accounts, insurances and credit cards organised in only one space. With the app, you will be able to know how much you are spending.

This script imports the daily expenditure into exist.io, ignoring certain recurrent categories (like rent or direct debit for internet provider or electricity) not aligned to your behaviour. The idea is to store in exist.io only the money spent on restaurants, clothes you buy, or anything linked to things you do, rather than automated transfers.

### Google Photos

This integration imports into exist.io the number of pictures taken every day (and uploaded to Google Photos). The idea is that those days with more activity or happiness are normally those days you take more pictures. It uses the Google Photos API.

### Google Location History

This integration imports data into exist.io but it is still in progress: number of different locations and number of kilometers travelled by car. There is not an API for Google Location history so we use Google Takeout to download an extract and import it.

### Stock Market

This integration stores values the close value for some tickers into exist.io

## How to add a new service

Once you create your account in exist.io, you need to follow the next steps to be able to use the data. This section might get out of date quick, so please only use for quick reference, the real instructions are in Exist.io API documentation (https://developer.exist.io/).

### Create client 

You do this on their website, just enter the details about the new service.

https://exist.io/account/apps/

On the redirect URI you can enter https://localhost/ (make sure you don't forget the httpS)

Once you create the new app, you will get a CLIENT ID and a CLIENT SECRET. You will use them in a second.

### Authorise, by opening in chrome the following URL 

https://exist.io/oauth2/authorize?response_type=code&client_id=ZZZ&redirect_uri=https://localhost/&scope=read+write

Replace ZZZ in the URL above with the CLIENT ID you got in the previous step.

Watch the URL! You  will get a code you will use in the next step, something like 4cxc4c0fa210xxxc28ce19a8b079eb67d9x19c1c

### Get bearer token

In python you can do something like the below, where ABC is the code you got in the previous step. The client id and client secret come from the first step.

```python
import requests
url = 'https://exist.io/oauth2/access_token'
response = requests.post(url,
           {'grant_type':'authorization_code',
            'code': "ABCD",
            'client_id': "DEFG",
            'client_secret': "HIJK",
            'redirect_uri':"https://localhost/" })
```

The response.content will be something like:

```
{"access_token": "zzzzzzzzc40c9157ae75f777bd6e856aee6", "token_type": "Bearer", "expires_in": 31535999, "scope": "read write read+write", "refresh_token": "xxxxxxx766ef2d083b515d7d988aa36ef470ba9d"}
```

This bearer token will be valid for a period of time, after it expires you will need to get another one. There is one extra step before start putting data into exist.io, activate the attribute...

### Activate the attribute

The following code needs to be run to activate the attribute for your application (first time only). It uses the bearer token you got previously.

```python
import requests
url = 'https://exist.io/api/1/attributes/acquire/'
attributes = [{"name":"ATTRIBUTE_NAME", "active":True}]
response = requests.post(url, headers={'Authorization':'Bearer zzzzzzzzc40c9157ae75f777bd6e856aee6', 'Content-Type': 'application/json; charset=utf-8'},data=json.dumps(attributes))
```

After this you will be able to upload data into the system and see it.
