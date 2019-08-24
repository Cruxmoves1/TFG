"""
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% TFG: Vigilancia Tecnológica y Minería de Opiniones en RRSS
% Escuela Técnica Superior de Ingenierías Informática y de Telecomunicación
% Realizado por: Miguel Keane Cañizares
% Contacto: miguekeca@correo.ugr.es
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""

#Este código es para cuando el análisis se ha interrumpido por la razón que sea y se desea continuar desde el último usuario analizado.

from pymongo import MongoClient
import json
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import datetime
import requests
import csv
import os.path

# Conectamos MongoDB la base de datos "TwitterStream"
connection = MongoClient('localhost', 27017)
db = connection.TwitterYT2108
db.tweets.create_index("id", unique=True, dropDups=True)
collection = db.tweets
collection2 = db.concepts

# Conectar a la API externa que hara el analisis de sentimientos

url = "https://api.meaningcloud.com/sentiment-2.1"

key= "YOUR_KEY"
lang="en"
headers = {'content-type': 'application/x-www-form-urlencoded'}


#Me aserguro que el archivo no exista previamente, para no escribir varias veces los titulos
if not os.path.exists('data/YT2108.csv'):
    with open('data/YT2108.csv', 'w') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',')
        filewriter.writerow(['Username', 'Followers', 'Confidence', 'Score_tag', 'Agreement', 'Subjectivity', 'Irony', 'Tweet'])
#
#cursors = db.collection.find();
control = False

#Para cuando el nombre se ha repetido dos veces
#control2 = True
for cursor in db.tweets.find():
      tweet = cursor.get('text')
      username = cursor.get('username')
      if control:
          followers = cursor.get('followers')
          id = cursor.get('tweet_id')

          print (username + ': ' + tweet)
          #payload= "key="+key+"&lang="+lang+"&txt="+txt
          payload = "key=YOUR_KEYe&lang=en&of=json&txt= %s &txtf=plain&url=YOUR_URL_VALUE&doc=YOUR_DOC_VALUE" %(tweet)
          confidence= 0
          #Manejo excepciones por si la conexion da error que siga analizando la base de datos MongoDB
          try:
              response = requests.request("POST", url, data=payload, headers=headers)
              print(response.text)
              answer = json.loads(response.text)
              code = answer['status']['code']
              if int(code)!=212:
                  confidence = answer['confidence']
                  score_tag= answer['score_tag']
                  agreement= answer['agreement']
                  subjectivity = answer['subjectivity']
                  irony = answer['irony']
                  sentimented_entity_list = answer['sentimented_entity_list']
                  sentimented_concept_list = answer['sentimented_concept_list']
                  quoted_tweet = '"{}"'.format(tweet)
                  #Me aseguro que la confianza en el analisis este en un rango aceptable
                  if int(confidence) > 90:
                      try:
                          concepts = {'id': id, 'score_tag':score_tag, 'entities': sentimented_entity_list, 'concepts':sentimented_concept_list, 'user':username , 'followers': followers, 'text': tweet}
                          collection2.save(concepts)
                          del concepts
                      except:
                            print("\n\n\n\n\n\nError al guardar en la base de datos MongoDB\n\n\n\n\n\n")

                      #El parametro a es para "append", para actualizar el csv en vez de sobrescribirlo
                      with open('data/YT2108.csv', 'a') as csvfile:
                          filewriter = csv.writer(csvfile, delimiter=',')
                          filewriter.writerow([username, followers, confidence, score_tag, agreement, subjectivity, irony, quoted_tweet])


                  else:
                      print("La confianza es demasiado bajo. Analisis no fiable \n\n\n\n")
          except ValueError:
            print("\nException: Failed request to API in meaningcloud. Wrong characters.")

      elif username== "CazallaLiebana":
          control=True
