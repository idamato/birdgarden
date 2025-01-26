from wordpress_scripts import wordpress_header
from wordpress_scripts import postmedia
from wordpress_scripts import postmedia4video
from wordpress_scripts import create_wordpress_post
import sys
import os
from datetime import datetime

#now = datetime.now()
#formatted_date_time = now.strftime("%Y%m%d%H%M%S")

seriale = sys.argv[1]
datafile = sys.argv[2]
media = sys.argv[3]

wp_user = "INSERT-WORDPRESS-USERNAME"
wp_pw = "INSERT-WORDPRESS-APPLICATION-PASSWORD"

# Esempio da adeguare al contesto
url = "www.webradiofaro.it/birdgarden" #you set the root domain of your WordPress site
filename = seriale + "." + datafile + media #you set the name of your image
categories = [2] # birdgarden
tags = [3] #identificare il tag con la CPUID (seriale) del Raspberry mittente, creato al momento dell'iscrizione

print("URL: " + url)
print("Media: " + media)
print("Filename: " + filename)

#authentication
wordpress_head_post = wordpress_header(wp_user, wp_pw)[0]
wordpress_auth_media = wordpress_header(wp_user, wp_pw)[1] 

ext = os.path.splitext(media)[-1].lower()
if ext == ".jpg":
     title = "Foto scattata dal Birdgarden " + seriale + " con timestamp " + datafile
     body = "<a href=\"Immagine originale\"><img src=\"https://www.webradiofaro.it/birdgarden/wp-content/uploads/" + filename + "\"></a>"
     #image upload
     media_id = postmedia(url, media, filename, wordpress_auth_media)
     #post creation
     create_wordpress_post(url, title, body, media_id, categories, tags, wordpress_head_post)
elif ext == ".mp4":
     title = "Video scattato dal Birdgarden " + seriale + " con timestamp " + datafile
     body = "<figure class=\"wp-block-video\"><video controls src=\"https://www.webradiofaro.it/birdgarden/wp-content/uploads/" + filename + "\" type=\"video/mp4\"></video></figure>"
     #video upload
     media_id = postmedia4video(url, media, filename, wordpress_auth_media)
     #post creation
     create_wordpress_post(url, title, body, media_id, categories, tags, wordpress_head_post)
else:
     #formato non supportato
     print(ext, " formato non supportato")
