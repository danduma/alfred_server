# This file syncs the local state of the code with the remote server. Essentially: deploy to production

SERVER=${1:-15.236.137.230} 
KEY=albert_server.pem
USER=ubuntu
USER_HOME=home/ubuntu
REPO_NAME=albert_server

rsync -v -e "ssh -i $KEY" --progress -r . $USER@$SERVER:/$USER_HOME/$REPO_NAME --exclude={'*.pyc','__pycache__','__pycache__/*','config.env','.DS_Store','.DS_Store/*','.webassets-cache/*','.webassets-external/*','node_modules/*','node_modules','db.sqlite3','.venv','data/*','.git','.idea/','*.tmp','db/*'}
ssh $USER@$SERVER -i $KEY 'sudo systemctl restart albert'
