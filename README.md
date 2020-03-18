# QA-engine
QA-engine is a question-answering service that wraps multiple QA models.

## Quick start

### Requirements
```
Python 3
Python 2.7 (qa-bert dependency)
```

### Cloning the project
Clone the repository with
```
git clone https://github.com/TrentoCrowdAI/qa-engine/
```

### Create python virtual environment
```
virtualenv -p python3 venv3.7
```

### Configure the project
First of all create your config.json file. Reference: TODO:link
Copy and paste the config.example.json in the root of the project.
```
cp config.example.json config.json
```

You can choose to configure the project automatically or manually, as you want.

#### Automatically
Start the script "service_start.sh" with:
```
bash service_start.sh
```
All the requirements will be downloaded and installed. If all goes well, the service API service is started on port 80.

#### Manually
If you want to have full control on the preparation of the environment you have to follow these steps:
1. Enter in the python virtual environment
`source venv3.7/bin/activate`
2. Download python dependencies
`pip install -r requirements_python2.txt`
`pip3 install -r requirements_python3.txt`
3. Download QA-models resources
`bash prepare_environment.sh`

### Start the QA-engine
For testing purposes you can launch:
`python3 app.py`
The API service will listen on port 5000.

Otherwise, in production environment you can run the service in background with:
`bash service_start.sh`
The API service will listen on port 80.


# Read the WIKI
[QA-Engine Wiki](https://github.com/TrentoCrowdAI/qa-engine/wiki)