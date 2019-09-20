#!/usr/bin/env python3
# scrape telegram => post to Discourse
import os
import time
import requests
import telepot
import magic

# used for filetype detection
if os.name == 'nt':
	mime = magic.Magic(magic_file="C:/Windows/System32/magic.mgc", mime=True)
else:
	mime = magic.Magic( mime=True)

# telegram constants
TOKEN = "xx"
DIR = "./images/"
#REGISTERED_CHATS = [x, -xx] 

# discourse constants
BASE_URL = "https://xx.xx/"
API_USER = 'xx'
API_KEY = 'xx'
AUTH_STRING = '?api_key=' + API_KEY+'&api_username=' + API_USER
TOPIC_ID = 68

# register the bot
bot = telepot.Bot(TOKEN)

def handle(msg):
	"""general handler for telegram messages"""
	content_type, chat_type, chat_id = telepot.glance(msg)

	if chat_id in REGISTERED_CHATS:
		if content_type is "photo":
			print("Photo message: " + str(msg))

			# download image
			local_filename = download_image(msg['photo'][-1]['file_id'])
			if local_filename:
				post_file(local_filename)
		else:
			print("Skipping other: " + str(msg))
	else:
		print("Skipping message from non registered chat" + str(msg))


def download_image(file_id):
	"""download an image from telegram to the local file system"""
	new_name = None
	file_name = DIR + file_id
	bot.download_file(file_id, file_name)

	if os.path.isfile(file_name):
		new_name = rename_file(file_name)
	return new_name


def rename_file(file):
	"""detect the mimetype of images with magic and rename them"""
	new_name = None

	file_name, extension = os.path.splitext(file)
	if extension == "":
		mime_type = mime.from_file(file)
		if mime_type == "image/jpeg":
			new_name = file + ".jpg"
		elif mime_type == "image/png":
			new_name = file + ".png"
		elif mime_type == "image/gif":
			new_name = file + ".gif"
		else:
			print("unmapped mime: " + mime_type)
	if new_name and not os.path.isfile(new_name):
		os.rename(file, new_name)
	return new_name


def post_file(file_name):
	"""post the file to discourse thread"""
	file_url = upload_file(file_name)
	if file_url is not None:
		try:
			url = BASE_URL + 'posts'
			data = dict(raw="<img src=\"" + file_url + "\">", topic_id=TOPIC_ID, api_key=API_KEY, api_username=API_USER)

			r = requests.post(url, data=data)
			json_response = r.json()
			print(json_response)
		except Exception as e:
			print("Failed to make post")
			print(e)


def upload_file(file_name):
	"""upload a local file to discourse and return the URL"""
	file_url = None

	try:
		print("Uploading: " + file_name)
		url = BASE_URL + 'uploads.json' + AUTH_STRING + '&synchronous=1'
		files = {'file': open(file_name, 'rb')}
		data = dict(type='composer', client_id='1234b591bb4848dd899b6e6ee0feaff9')

		r = requests.post(url, files=files, data=data)
		json_response = r.json()

		if json_response is not None:
			# extract the uploaded file URL from the response
			print(json_response)
			file_url = json_response['url']
	except Exception as e:
		print("Failed to upload file")
		print(e)
	return file_url
	
def main():
	print('Listening ...')
	try:
		bot.message_loop(handle)
	except Exception as e:
		print(e)

	while True:
		time.sleep(10)


if __name__ == '__main__':
	main()
