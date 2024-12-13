#Use python3.9 slim
FROM python:3.9-slim

#Set the working directory
WORKDIR /app

#Install flask
RUN pip install flask

#Copy application code and database schemas
COPY . .

#Expose port 5003 for flask
EXPOSE 5003

#Set the command to run our app
CMD ["python", "users.py"]