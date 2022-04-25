
#!/bin/bash

sudo apt-get install python3-virtualenv

virtualenv -p python3 venv

source venv/bin/activate

pip install -r requirements.txt

source venv/bin/activate