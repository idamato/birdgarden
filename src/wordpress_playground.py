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

# Memorizzo le stringhe per l'anno ed il mese che utilizzerò in seguito
annofile = datafile[:4]
mesefile = datafile[4:6]

# Le informazioni seguenti devono essere fornite dall'amministratore del portale web www.webradiofaro.it/birdgarden/
# Per informazioni e richiesta di un account inviare mail a info@webradiofaro.it con il seriale del proprio Raspberry (cat /proc/cpuinfo | grep Serial)
wp_user = "INSERT-WORDPRESS-USERNAME"
wp_pw = "INSERT-WORDPRESS-APPLICATION-PASSWORD"
categories = [2] # Al momento esiste l'unica categoria birdgarden ma in futuro potranno essere distinti i nidi dalle mangiatoie, o altro
tags = [3] #identificare il tag con la CPUID (seriale) del Raspberry mittente, creato al momento dell'iscrizione

# Esempio da adeguare al contesto
url = "www.webradiofaro.it/birdgarden" #you set the root domain of your WordPress site
# costruisco il nome del file con i separatori
filename = seriale + "." + media 

print("URL: " + url)
print("Media: " + media)
print("Filename: " + filename)

values = filename.split('.')
significativi = values[1].split('_')
ts, luce, temperatura, audio, sonar = [(value) for value in significativi]
print(ts, luce, temperatura, audio, sonar)

# authentication
wordpress_head_post = wordpress_header(wp_user, wp_pw)[0]
wordpress_auth_media = wordpress_header(wp_user, wp_pw)[1] 

ext = os.path.splitext(media)[-1].lower()
if ext == ".jpg":
     title = "Foto dal Birdgarden " + wp_user + " del " + datafile
     # La seguente variabile potrebbe cambiare in base alle impostazioni del sito wordpress
     # Nel caso in cui le immagini ed i video vanno a finire in una unica directory non organizzata usare la riga seguente per costruire il link
     body = "<a href=\"https://www.webradiofaro.it/birdgarden/wp-content/uploads/" + filename + "\">Immagine originale</a><p>ID: " + ts + "<br>Temperatura: " + temperatura + "<br>Luce: " + luce + "<br>Rumore: " + audio + "<br>Distanza: " + sonar + "</p>" 
     # Se invece tutti i media vanno a finire in sottodirectory classificate per anno e mese, usare la seguente
     # body = "<a href=\"https://www.webradiofaro.it/birdgarden/wp-content/uploads/" + annofile + "/" + mesefile + "/" + filename + "\">Immagine originale</a><p>ID: " + ts + "<br>Temperatura: " + temperatura + "<br>Luce: " + luce + "<br>Rumore: " + audio + "<br>Distanza: " + sonar + "</p>"   
     #image upload
     media_id = postmedia(url, media, filename, wordpress_auth_media)
     #post creation
     create_wordpress_post(url, title, body, media_id, categories, tags, wordpress_head_post)
elif ext == ".mp4":
     title = "Video dal Birdgarden " + wp_user + " del " + datafile
     # Nel caso in cui le immagini ed i video vanno a finire in una unica directory non organizzata usare la riga seguente per costruire il link
     body = "<figure class=\"wp-block-video\"><video controls src=\"https://www.webradiofaro.it/birdgarden/wp-content/uploads/" + filename + "\" type=\"video/mp4\"></video></figure><p>ID: " + ts + "<br>Temperatura: " + temperatura + "<br>Luce: " + luce + "<br>Rumore: " + audio + "<br>Distanza: " + sonar + "</p>" 
     # Se invece tutti i media vanno a finire in sottodirectory classificate per anno e mese, usare la seguente
     # body = "<figure class=\"wp-block-video\"><video controls src=\"https://www.webradiofaro.it/birdgarden/wp-content/uploads/" + annofile + "/" + mesefile + "/" + filename + "\" type=\"video/mp4\"></video></figure><p>ID: " + ts + "<br>Temperatura: " + temperatura + "<br>Luce: " + luce + "<br>Rumore: " + audio + "<br>Distanza: " + sonar + "</p>"
     #video upload
     media_id = postmedia4video(url, media, filename, wordpress_auth_media)
     #post creation
     create_wordpress_post(url, title, body, media_id, categories, tags, wordpress_head_post)
else:
     #formato non supportato
     print(ext, " formato non supportato")
