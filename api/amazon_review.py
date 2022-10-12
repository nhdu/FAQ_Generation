import requests
import json
import time
class AmazonAPI():
    
    headers = {
	"X-RapidAPI-Key": "6a2a93192cmshb0ca40c9b880c29p12444bjsn017d0a61074d",
	"X-RapidAPI-Host": "amazon-product-reviews-keywords.p.rapidapi.com"
    }
    
    url = "https://amazon-product-reviews-keywords.p.rapidapi.com/product/reviews"
    
    def get_reviews(self, pages: int, asin: str, country: str = "AU", variants: str = "0", top : str = "0"):
        ''' 
        Return a list of product reviews text
            Parameters:
                    pages (int): the number of review pages. 
                    asin (string): product's ASIN number. 
                    
                    country (string): marketplace country. (default: AU)
                    
                    variants (string): 1 - reviews for all product variants.
                                       0 - reviews only for specified product ASIN (default).
                                       
                    top (string):      0 - reviews will be sorted by "Most recent" (default).
                                       1 - reviews will be sorted by "Top reviews".
        '''
        try: 
            print(asin)
            reviews_list = []
            for i in range(1, pages + 1):
                response = requests.request("GET", self.url, headers= self.headers, params={"asin":asin, "page": str(i), "country": country,"variants":variants,"top":top}, timeout=10)
                print(response)
                reviews = json.loads(response.text)["reviews"]
                for review in reviews: 
                    reviews_list.append(review["review"])
                    print(review["review"])
                    print(i)    
            return reviews_list
        except:
            error_message = "Error: There has been an error. Please make sure to provide the right ASIN number!"
            return error_message
        
            
       