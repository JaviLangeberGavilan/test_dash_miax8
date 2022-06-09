FROM public.ecr.aws/lambda/python:3.8

# Set the working directory in the container
WORKDIR /code

# Copy the dependences
COPY requirements.txt .
RUN pip install -r requirements.txt


COPY /src .

EXPOSE 8080
CMD ["python", "app.py"]
