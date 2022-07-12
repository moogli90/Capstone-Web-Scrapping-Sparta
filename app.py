from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.imdb.com/search/title/?release_date=2021-01-01,2021-12-31')
soup = BeautifulSoup(url_get.content,"html.parser")

#find your right key here
table = soup.find("div", attrs={"class":"lister-item mode-advanced"})
table = soup.findAll("div", attrs={"class":"lister-item mode-advanced"})

row_length = len(table)

temp = [] #initiating a list 

for store in table:
    #get movie name
    movie_name = store.h3.a.text
    
    #get rating
    rating = store.find("div", class_="inline-block ratings-imdb-rating").text.replace("\n", "")
    
    #get metascore
    metascore = store.find("span", class_="metascore").text.replace(" ","") if store.find("span", class_="metascore") else "00"
    
    #get vote
    value=store.find_all('span',attrs={"name":"nv"})
    vote=value[0].text
    
    #get gross
    gross=value[1].text if len(value) >1 else '00,00'
    
    temp.append((movie_name,rating,metascore,vote,gross))

#change into dataframe
df = pd.DataFrame(temp, columns = ("movie_name","rating","metascore","vote","gross")).iloc[0:7 , 0:4]

#insert data wrangling here
df["rating"]=df["rating"].astype("float64") #mengubah tipe data
df["metascore"]=df["metascore"].astype("int64")
df["vote"]=df["vote"].str.replace(",","") #melakukan adjustment agar data bisa diubah menjadi tipe int
df["vote"]=df["vote"].astype("int64")
df=df.head(7)
df=df.set_index("movie_name")

#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'{df["rating"].mean().round(2)}' #be careful with the " and ' 

	# generate plot
	ax = df.plot(figsize = (20,9)) 
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)