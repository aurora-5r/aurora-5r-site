while true
do
    rsync -avz  /home/ec2-user/dev/aurora2.0/dist/*  /var/www/html/
    sleep 5
done
