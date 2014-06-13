import redis
import requests

r = redis.StrictRedis(host='localhost', port=6379, db=0)

def get(url):
	val = r.get(url)
	if val is None:
		val = requests.get(url)
		r.set(url,val.text.encode("ascii", "ignore"))
		val = val.text.encode("ascii","ignore") 
	
	return val

def get_cache(url):
	val = r.get(url)
	return val
