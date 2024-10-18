Not uploading the generated layer file but the steps to generate are:

git clone https://github.com/imperva/aws-lambda-layer.git
cd aws-lambda-layer
python3 src/create_layer.py -l sklearn


Then copy the generated .zip file from the output folder into this folder.