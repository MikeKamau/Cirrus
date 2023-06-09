#This Dockerfile is for educational purposes and generates an image that utilizes the inbuilt flask webserver.
#For production purposes you should use Gunicorn and Nginx and create a user to run the app that is not root for security resasons.
#This Dockerfile and the accompanying env.txt file that set the values of the environment variables used by the app should be moved out of the Cirrus folder so that they are on the same directory level i.e.
#
#   ParentDirectory/
#       |
#       |___Dockerfile
#       |___env.txt
#       |___Cirrus/
#
#You can then create the image file by running the "docker image build -t cirrusimage ." command from within the ParentDirectory.
#Once the image is created successfully you can then run the "docker run -p 5000:5000 --env-file envs.txt cirrusimage" command to start up a container running the app.

FROM continuumio/miniconda3

COPY ./Cirrus /Cirrus/
WORKDIR /Cirrus

# Create the conda environment
RUN conda env create -f environment.yml \
    && echo "source activate cirrus" > ~/.bashrc

# Activate the conda environment
SHELL ["conda", "run", "-n", "cirrus", "/bin/bash", "-c"]

# Set the entrypoint
ENTRYPOINT ["/opt/conda/envs/cirrus/bin/flask", "run", "--host=0.0.0.0"]

# Expose port 5000 to access the app
EXPOSE 5000