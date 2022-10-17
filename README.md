### **Overview:**
In this project, a cloud application to was developed that helps recognise individuals in videos. It is developed on the PAAS cloud service of the Amazon Web Service which is Lambda. 
The users of this application would upload files to an S3 bucket. Each time a video is uploaded to this bucket, the lambda code gets triggered. This function then downloads that video, extracts images from it, performs facial recognition on the frames, queries details of the resultant person and uploads the results to the output s3 bucket in the form of a CSV file.

The language used is *Python* and the package used to create, process and destroy AWS cloud functionalities is *boto3*. The *ffmpeg* and *face_recognition* packages are used to creating frames from the video and perform facial recognition on these frames respectively.
To run it, the docker file provided is used to create an image and upload to the ECR that is in-turn used to build the lambda function upon.

### **AWS component details:**
```
AWS Lambda Name:             new_image_recognition
AWS S3 input bucket:         myinputbucket
AWS S3 ouput bucket:         myoutbucket
AWS DynamoDB table:          new_students
```

### **Execution Instructions:**
1. Install Python.
2. Install boto3 and awscli packages.
3. Open the workload.py file and change the input and output bucket variables to point to the correct values as mentioned above.
4. Execute the workload file to upload videos to the input bucket. This triggers the lambda function to exectute.
```
python workload.py
```
5. Open the output bucket on the browser to find the respective academic records being generated.
