# vagrant ssh
# python3 manage.py runserver 0.0.0.0:8000

# После обновления из репозитория:
# vagrant provision
# vagrant ssh
# python3 manage.py runserver 0.0.0.0:8000

Vagrant.configure(2) do |config|
  config.vm.box = "ubuntu/trusty64"
  config.vm.network "forwarded_port", guest: 8000, host: 8000
  config.vm.provision "shell", inline: <<-SHELL
     sudo apt-get update;
     sudo apt-get install -y libxml2-dev libxslt1-dev python3-dev python3-setuptools python3.4 build-essential python3-pip nginx libpq-dev mysql-client libmysqlclient-dev;
     sudo su;
     cd /vagrant;
     pip3 install -r requirements.txt;
     python3 manage.py migrate --noinput;
  SHELL
end
