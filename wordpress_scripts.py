import requests
import base64

#token creation function, for authentication purposes
def wordpress_header (wp_user, wp_pw):

 wordpress_credentials = wp_user + ":" + wp_pw
 wordpress_token = base64.b64encode(wordpress_credentials.encode())
 wordpress_header = {'Authorization': 'Basic ' + wordpress_token.decode('utf-8')}
 wordpress_auth = wordpress_token.decode('utf-8')

 return wordpress_header, wordpress_auth


#post media function
def postmedia (url, media, filename,wordpress_auth_media):

    Headers =  {
        'Authorization': f'Basic {wordpress_auth_media}',
        "Content-Disposition": f"attachment; filename={filename}.jpg",
        'Content-Type': 'multipart/form-data',
        'Cache-Control' : 'no-cache'
                }

    api_url = f"https://{url}" + "/wp-json/wp/v2/media/"

    mediaImageBytes = open(media, 'rb').read()

    response = requests.post(api_url, headers=Headers, data=mediaImageBytes)

    results = response.json()

    return results["id"]

#post creation function
def create_wordpress_post(url, title, body,image_id, categories, tags, wordpress_header_post):

 api_url = f'https://{url}/wp-json/wp/v2/posts'

#data structure of the post, in JSON
 data = {
"title": title,
"content": body,
"featured_media": image_id,
"status": "publish",
"categories": categories,
"tags": tags
 }

 response = requests.post(api_url, headers=wordpress_header_post, json=data)

 result = response.json()

# You can uncomment this line if you want to print a confirmation of each post creation in the console
 print(result) 

 return result
