from wordpress_scripts import wordpress_header
from wordpress_scripts import postmedia
from wordpress_scripts import create_wordpress_post
import sys
from datetime import datetime

now = datetime.now()
formatted_date_time = now.strftime("%Y%m%d%H%M%S")

seriale = sys.argv[0]
datafile = sys.argv[1]
media = sys.argv[2]

wp_user = "INSERT-WORDPRESS-USERNAME"
wp_pw = "INSERT-WORDPRESS-APPLICATION-PASSWORD"

# Esempio da adeguare al contesto
url = "www.webradiofaro.it/wp" #you set the root domain of your WordPress site
# media = "images/000000008279d33b.2025010232901.3_75_21_37_3.jpg" #you set the location of the image you want to upload
filename = seriale + "." + datafile #you set the name of your image
title = "Il mio primo articolo generato con Python" #you set the title of your first WordPress post
body = "Quando le immagini parlano è inutile spendere troppe parole..."
categories = [97] # birdgarden
tags = [94] #identificare il tag con la CPUID (seriale) del Raspberry mittente, creato al momento dell'iscrizione

#authentication
wordpress_head_post = wordpress_header(wp_user, wp_pw)[0]
wordpress_auth_media = wordpress_header(wp_user, wp_pw)[1] 

#image upload
image_id = postmedia(url, media, filename, wordpress_auth_media)
print(image_id)

#post creation
create_wordpress_post(url, title, body, image_id, categories, tags, wordpress_head_post)
