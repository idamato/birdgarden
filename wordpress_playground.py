from wordpress_scripts import wordpress_header
from wordpress_scripts import postmedia
from wordpress_scripts import create_wordpress_post
import sys

serial = sys.argv[0]
sensor_data = sys.argv[1]
media = sys.argv[2]

wp_user = "INSERT-WORDPRESS-USERNAME"
wp_pw = "INSERT-WORDPRESS-APPLICATION-PASSWORD"

# Esepio da adeguare al contesto
url = "www.webradiofaro.it/wp" #you set the root domain of your WordPress site
# media = "images/000000008279d33b.2025010232901.3_75_21_37_3.jpg" #you set the location of the image you want to upload
filename = "gazometro" #you set the name of your image
title = "Il mio primo articolo generato con Python" #you set the title of your first WordPress post
body = "Quando le immagini parlano è inutile spendere troppe parole..."
categories = [97] #11 being for instance the "Coding" category on your site
tags = [94] #2 being for instance the "Python" tag on your site

#authentication
wordpress_head_post = wordpress_header(wp_user, wp_pw)[0]
wordpress_auth_media = wordpress_header(wp_user, wp_pw)[1] 

#image upload
image_id = postmedia(url, media, filename, wordpress_auth_media)
print(image_id)

#post creation
create_wordpress_post(url, title, body, image_id, categories, tags, wordpress_head_post)
