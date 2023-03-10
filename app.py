from flask import Flask , render_template ,jsonify, request
from flask_cors import CORS , cross_origin
from bs4 import BeautifulSoup as bs
import requests
from urllib.request import urlopen
import logging
import pymongo
logging.basicConfig(filename="web_scrapper.log",level=logging.INFO,format="%(asctime)s,%(levelname)s,%(message)s")
app = Flask(__name__)

@app.route("/",methods=['GET'])
def homepage():
    logging.info("Homepage showed")
    return render_template("index.html")
@app.route("/review",methods=['POST' , 'GET'])
def web_scrapper():
    if (request.method == 'POST'):
        try:
            search_string = request.form['content']
            logging.info(f"Reviews need to scrap for {search_string}")
            url_string = search_string.replace(" ","")
            flipkart_url = "https://www.flipkart.com/search?q="+url_string
            unclient = urlopen(flipkart_url)
            flipkart_sorce = unclient.read()
            flipkart_html = bs(flipkart_sorce,"html.parser")
            bigbox = flipkart_html.find_all("div",{"class":"_1AtVbE col-12-12"})
            del bigbox[0:3]
            box = bigbox[0]
            product_link = "https://www.flipkart.com"+ box.div.div.div.a["href"]
            product_url= urlopen(product_link)
            product_req = product_url.read()
            product_html = bs(product_req,"html.parser")
            comment_boxes = product_html.find_all("div",{"class":"_16PBlm"})
            reviews = []
            for comment_box in comment_boxes:
                try:
                    name = comment_box.div.div.find_all("div",{"class":"row _3n8db9"})[0].div.p.text
                except Exception as e:
                    name = "out of reviewers"
                    logging.info(name)
                try:
                    rating = comment_box.div.div.find_all("div",{"class":"_3LWZlK _1BLPMq"})[0].text
                except Exception as e:
                    rating = "out of rating"
                    logging.info(rating)
                try:
                    comment_head = comment_box.div.div.find_all("p",{"class":"_2-N8zT"})[0].text
                except Exception as e:
                    comment_head = "Out of comments"
                    logging.info(comment_head)
                try:
                    comment = comment_box.div.div.find_all("div",{"class":""})[0].text
                except Exception as e:
                    comment = "Out of comment"
                    logging.info(comment)
                mydict = {'Product':search_string,'Name':name,'Rating':rating,'CommentHead':comment_head,'Comment':comment}
                reviews.append(mydict)
            logging.info(f"The final data is: {reviews}")
            client = pymongo.MongoClient("mongodb+srv://JEHAD:rj912865@rj.qerdyzm.mongodb.net/?retryWrites=true&w=majority")
            db = client['scraping']
            c = db["web_scraping"]
            c.insert_many(reviews)
            return render_template("result.html",reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            logging.exception(e)
            return "Something is wrong"
    else:
        return render_template("index.html")

if __name__=="__main__":
    app.run("0.0.0.0",port=8080)
