from boto3 import client as boto3_client
import face_recognition
import pickle
import json
import urllib.parse
import os, csv

input_bucket = "myinputbucket"
output_bucket = "myoutbucket"
ac1 = str(os.getenv("ac1"))
ac2 = str(os.getenv("ac2"))
REGION_NAME = "us-east-1"
s3_client = boto3_client('s3', aws_access_key_id=ac1, aws_secret_access_key=ac2, region_name=REGION_NAME)
db_client = boto3_client('dynamodb', aws_access_key_id=ac1, aws_secret_access_key=ac2, region_name=REGION_NAME)

# Function to read the 'encoding' file
def open_encoding(filename):
	file = open(filename, "rb")
	data = pickle.load(file)
	file.close()
	return data

def random_stuff_remove():
	known_image = face_recognition.load_image_file("/tmp/img0.jpeg")
	unknown_image = face_recognition.load_image_file("/tmp/img0.jpeg")

	biden_encoding = face_recognition.face_encodings(known_image)[0]
	unknown_encoding = face_recognition.face_encodings(unknown_image)[0]

	results = face_recognition.compare_faces([biden_encoding], unknown_encoding)
	print("results", results)


def face_recognition_handler(event, context):	
	print("EVENT", event)
	print("CONTEXT[", context)
	print("--"*20)
	
	print("\ngot environments\n")

	# os.system("sudo chmod 777 .")
	# os.system("mkdir tmp")
	# os.system("sudo chmod 777 .")

	# get the latest file from the S3 bucket into the tmp folder
	try:
		# input_file_name = event["Records"][0]["s3"]["object"]["key"] #include .mp4
		bucket = event['Records'][0]['s3']['bucket']['name']
		input_file_name = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
		filepath = "/tmp/"+input_file_name
		print("SO THIS IS HERE", input_file_name)
		s3_client.download_file(input_bucket, input_file_name, filepath)
		# response = s3_client.get_object(Bucket=bucket, Key=input_file_name)
		# print("CONTENT TYPE: " + response['ContentType'])
	except Exception as e:
		print("Cannot get the input file")
		print(e)
		print()
	print("------ A ------")

    # Extract a frame from the video
	os.system("ffmpeg -skip_frame nokey -i "+str(filepath)+"  -vsync 0 -frame_pts true /tmp/img%d.jpeg")
	print("------ B ------")

    # perform face_recognition on the frame
	# random_stuff_remove()
	ec_file = os.path.basename("encoding")
	known_encoding = open_encoding(ec_file)
	unknown_image = face_recognition.load_image_file("/tmp/img0.jpeg")
	unknown_encoding = face_recognition.face_encodings(unknown_image)[0]
	# if type(known_encoding)!='list':
	# 	known_encoding = [known_encoding]
	print("KNOWN ENCODING TYPE:",type(known_encoding))
	# print("KNOWN ENCODING:",known_encoding)
	print("UNKNOWN ENCODING TYPE:",type(unknown_encoding))
	# print("UNKNOWN ENCODING:",unknown_encoding)
	result = face_recognition.compare_faces(known_encoding['encoding'], unknown_encoding)
	recognised = str(known_encoding['name'][result.index(True)])

	# result = "johnny_dep"
	print("------ C ------")

	# Get the db response related to the person in te image
	data = db_client.get_item(
      TableName = 'new_students',
      Key = {
          'name': {'S': recognised}
    })
	print(recognised, data)
	print("------ D ------")

	# upload the response to S3
	x = input_file_name.split('.')[0]+'.csv'
	res_major = data['Item']['major']['S']
	res_year = data['Item']['year']['S']
	res_header = ['name','major','year']
	res_data = [recognised,res_major, res_year]
	with open("/tmp/"+x, 'w', encoding='UTF8') as f:
		writer = csv.writer(f)
		# write the header
		writer.writerow(res_header)
		# write the data
		writer.writerow(res_data)
	object_name = os.path.basename(x)
	response = s3_client.upload_file("/tmp/"+x, output_bucket, object_name)
	print("------ E ------")


	# delete the file created and downloaded 
	print("LISTDIR BEFORE DELETE:")
	print(os.listdir("/tmp/"))
	c1 = "rm -rf /tmp/"+input_file_name
	os.system(c1)
	c1 = "rm -rf /tmp/"+x
	os.system(c1)
	os.system("rm -rf /tmp/img0.jpeg")
	print("LISTDIR AFTER DELETE:")
	print(os.listdir("/tmp/"))

	print("------ F ------")
	print("DONE!!!!!")