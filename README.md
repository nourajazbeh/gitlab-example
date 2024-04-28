# Gitlab CI/CD 
#### Ziel
Wir wollen eine einfache CI/CD Pipeline bauen.
### Was ist Gitlab CI/CD?
- Gitlab möchte DIE DevOps-Plattform werden, daher werden viele Features angeboten/unterstützt zum Planen, Implementieren, Testen, Paketieren, Releasen und Beobachten
- Großer Part ist die CI/CD Pipeline
- CI/CD Pipeline ist ein Prozess, der automatisiert wird, um Codeänderungen zu testen und zu überprüfen, bevor sie in Produktion gehen
- CI/CD Pipeline besteht aus mehreren Schritten, die automatisiert werden
- CI/CD Pipeline wird in einer Datei definiert, die in der Regel in der Wurzel des Projekts liegt
- Gitlab CI/CD ist in Gitlab integriert und wird in der Gitlab-Datei definiert
### Was ist CI/CD?
- CI/CD steht für Continuous Integration/Continuous Deployment bzw. Delivery
- Continuous Integration: Automatisches Zusammenführen von Codeänderungen in einem gemeinsamen Repository
- Continuous Deployment: Automatisches Bereitstellen von Codeänderungen in einer Produktionsumgebung
- Continuous Delivery: Automatisches Bereitstellen von Codeänderungen in einer Testumgebung
### Andere CI/CD-Tools
- Jenkins (immer noch viel verwendet)
- Github Actions
- CircleCI
- TravisCI
- Azure Pipelines
- AWS CodePipeline
...
##### Vorteil von Gitlab CI/CD
- Wir brauchen keine Extension für CI/CD
- ist einfach integriert ins Code Repository
- können wir selber hosten, oder aber als SaaS bzw. managed Service nutzen
- z.B. bei Jenkins müssten wir zunächst einen Jenkins Server einrichten, konfigurieren und dann die Pipeline definieren
### Gitlab Architektur
1. Gitlab Instanz bzw. Server (Gitlab.com oder eigene Instanz)
Der Gitlab-Server hostet den Anwendungscode und die Pipeline Konfiguration bzw. Gitlab Konfigurationen. Er organisiert also die Pipeline-Ausführung. Er "weiß was gemacht werden soll". Wir können einerseits `gitlab.com` nutzen oder aber eine eigene Instanz aufsetzen.
2. Gitlab Runner (Runner von Gitlab oder eigener Runner)
Einzelne Maschinen bzw. Agenten, die die CI/CD-Jobs dann ausführen. Sie sind die "Arbeiter" und führen die Pipeline aus. Wir können entweder die Runner von Gitlab nutzen oder aber eigene Runner aufsetzen. Gitlab bietet viele Runner an, die jeden User auf `gitlab.com` nutzen kann. Wir können aber auch eigene Runner aufsetzen, die dann in unserer Infrastruktur laufen.

## Beispiel: Flask-App CI/CD
Wir wollen eine einfache Flask-App bauen und deployen. Dafür wollen wir eine CI/CD Pipeline bauen. Wir wollen, dass die Pipeline folgende Schritte durchführt:
1. Testen der Flask-App
2. Bauen der Docker-Images
3. Pushen der Docker-Images
4. Deployen der Docker-Images mithilfe von Terraform-Template auf AWS

#### Einrichten des Gitlab-Accounts
1. Account auf `gitlab.com` erstellen
2. SSH Key hinzufügen
3. Python-Demo-App forken und in Gitlab importieren
4. Klonen des Gitlab Repositories

#### Die App schreiben
1. Erstelle in `src/app` eine neue python-Datei `app.py` und füge folgenden Code ein:
```
from flask import Flask, jsonify, request

app = Flask(__name__)

# Einfache Begrüßung
@app.route('/')
def hello():
    return "Hallo Welt!"

# Eine Route, die einen Namen als Parameter nimmt und begrüßt
@app.route('/hello/<name>')
def hello_name(name):
    return f"Hallo, {name}!"

# Eine JSON-Route, die Daten zurückgibt
@app.route('/data')
def data():
    return jsonify({'key': 'value', 'int': 1})

# Eine POST-Route, die Daten empfängt und etwas damit macht
@app.route('/post', methods=['POST'])
def post_data():
    data = request.json
    return jsonify(data), 201

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
```
2. Erstelle direkt eine Test-Datei `test_app.py` in `src/app` und füge folgenden Code ein:
```
import pytest
from flask_testing import TestCase
from app import app

class MyTest(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        return app

    def test_hello(self):
        response = self.client.get('/')
        self.assert200(response)
        self.assertEqual(response.data.decode(), "Hallo Welt!")

    def test_hello_name(self):
        response = self.client.get('/hello/Max')
        self.assert200(response)
        self.assertEqual(response.data.decode(), "Hallo, Max!")

    def test_data(self):
        response = self.client.get('/data')
        self.assert200(response)
        self.assertEqual(response.json, {'key': 'value', 'int': 1})

    def test_post_data(self):
        response = self.client.post('/post', json={'name': 'Tester'})
        self.assertStatus(response, 201)  # Überprüft, ob der Statuscode 201 ist
        self.assertEqual(response.json, {'name': 'Tester'})

# Führen Sie die Tests aus
if __name__ == '__main__':
    pytest.main()
```
3. Wir wollen als nächstes die Tests mal lokal ausführen und gucken, ob die Anwendung läuft. Dazu erstellen wir uns ein Virtual Environment und installieren die Dependencies:
```
python -m venv venv
source venv/bin/activate (in Windows: venv\Scripts\activate)
pip install -r requirements.txt
```
Danach testen, ob die Anwendung läuft mit:
```
python app.py
```
und testen, ob die Tests laufen mit:
```
pytest test_app.py
```
Nice, jetzt pushen wir das Ganze mal auf Gitlab.
#### Test-Stage hinzufügen
1. Erstelle eine `.gitlab-ci.yml` Datei im Root-Verzeichnis des Projekts und füge folgenden Code ein:
```
stages:
  - test


run_tests:
  stage: test
  image: python:3.12.3-bookworm
  before_script:
    - apt-get update && apt-get install -y python3-pip
    - pip install -Ur src/requirements.txt
  script:
    - pytest -v src
```
2. Commit und Push
3. Gehe auf Gitlab und schaue dir die Pipeline an
#### Docker-Image bauen und pushen
1. Erstelle eine `Dockerfile` im Root-Verzeichnis des Projekts und füge folgenden Code ein:
```
FROM python:3.12.3-bookworm

LABEL Name="Flask GitLab Demo App" Version=1.0.0


WORKDIR /app
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/app ./app

EXPOSE 5000

CMD ["python", "app/app.py"]
```
Als nächstes wollen wir in unserer Pipeline die Stages hinzufügen:
```
stages:
    - test
    - build
```
2. Wir brauchen allerdings noch ein paar Secrets, um das Ganze auch korrekt auf Docker-Hub zu pushen. Gehe dazu auf Gitlab -> Settings -> CI/CD -> Variables und füge folgende Variablen hinzu:
$DOCKER_USERNAME
Für den $DOCKER_TOKEN erstellen wir ein neues Access Token auf Docker-Hub und fügen es als Secret hinzu.
Lege in Docker-Hub ein neues Repository an. Den Image-Namen speichere bitte als Variable $IMAGE_NAME. Den Tag speichere bitte als Variable $IMAGE_TAG. Die Variablen werden wir in der Pipeline verwenden, d.h. wir müssen sie zu Beginn unserer Pipeline definieren.
```
variables:
    IMAGE_NAME: helenhaveloh/flask-gitlab
    IMAGE_TAG: python-app-1.0
```
3. Füge folgenden Code zur `.gitlab-ci.yml` Datei hinzu:
```
build_image:
    stage: build
    image: docker:26.1.0
    services:
        - docker:26.1.0-dind
    variables:
        DOCKER_TLS_CERTDIR: "/certs"
    before_script:
        - echo $DOCKER_TOKEN | docker login -u $DOCKER_USERNAME --password-stdin 
    script:
        - docker build -t $IMAGE_NAME:$IMAGE_TAG .
        - docker push $IMAGE_NAME:$IMAGE_TAG
```
Achtung: Wir wollen später den build and push-Step nur auf Tags machen.
4. Commit und Push
5. Gehe auf Gitlab und schaue dir die Pipeline an
#### Deployen der Docker-Images
1. Erstelle ein Terraform-Template `main.tf` im Root-Verzeichnis des Projekts und füge folgenden Code ein:
```
provider "aws" {
  region = "eu-central-1"
}

# Modul für das VPC
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws" 

  name = "PodInfoVPC"
  cidr = "10.0.0.0/16"

  azs             = ["eu-central-1a", "eu-central-1b", "eu-central-1c"]  
  public_subnets  = ["10.0.1.0/24"]
}

# Modul für die EC2-Instanz
module "ec2" {
  source  = "terraform-aws-modules/ec2-instance/aws"

  name           = "PodInfoInstance"
  ami            = "ami-0f7204385566b32d0"  # Ersetzen Sie dies durch eine gültige AMI-ID für Ihre Region
  instance_type  = "t2.micro"
  subnet_id      = module.vpc.public_subnets[0]
  vpc_security_group_ids = [aws_security_group.ec2-sg-podinfo.id]

  associate_public_ip_address = true
  user_data = <<-EOF
                #!/bin/bash
                sudo yum update -y
                sudo yum install -y docker
                sudo service docker start
                sudo docker run -d -p 80:5000 <docker_username>/<image_name>:<image_tag>
                EOF
}

resource "aws_security_group" "ec2-sg-gitlab" {
    name = "ec2-sg-gitlab"
    vpc_id = module.vpc.vpc_id

    ingress {
        from_port   = 80
        to_port     = 80
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }

    ingress {
        from_port   = 22
        to_port     = 22
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }

    egress {
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }
  
}

output "public_ip" {
  value = module.ec2.public_ip
}
```
Mit diesem Code erstellen wir eine EC2-Instanz und lassen unsere Flask-App darauf laufen, so dass wir sie über die öffentliche IP-Adresse erreichen können und ein helloworld sehen.
2. Füge folgenden Code zur `.gitlab-ci.yml` Datei hinzu:
Am Anfang nutzen wir ein template, um mit terraform zu deployen. 
```
include:
    - template: Terraform/Base.gitlab-ci.yml
```
Außerdem werden zwei neue Stages hinzugefügt. Einmal zum Initialisieren der Terraform-Dateien und einmal zum Deployen der EC2-Instanz.
```
stages:
    - test
    - build
    - init-tf
    - deploy
```
```
initialize_tf:
    stage: init-tf
    extends: .terraform:build

deploy_tf:
    stage: deploy
    extends: .terraform:deploy
    dependencies:
        - initialize_tf
    environment:
        name: $TF_STATE_NAME
```
Auch hier wollen wir das später nur auf Tags machen.
Damit das läuft, müssen wir allerdings noch unsere AWS_CREDENTIALS als Secret hinzufügen. Gehe dazu auf Gitlab -> Settings -> CI/CD -> Variables und füge folgende Variablen hinzu:
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_SESSION_TOKEN
3. Commit und Push
4. Gehe auf Gitlab und schaue dir die Pipeline an
Das Deployen der EC2-Instanz funktioniert noch nicht, da wir noch manuell den Job ausführen müssen. Das wollen wir aber nicht. Wir wollen, dass das automatisch passiert, wenn wir einen Tag pushen. Das machen wir jetzt.
#### Nur auf Tags deployen
1. Füge folgenden Code zur `.gitlab-ci.yml` Datei hinzu:
```
include:
    - template: Terraform/Base.gitlab-ci.yml


variables:
    IMAGE_NAME: helenhaveloh/flask-gitlab
    IMAGE_TAG: $CI_COMMIT_TAG

stages:
    - test
    - build
    - init-tf
    - deploy

run_tests:
  stage: test
  image: python:3.12.3-bookworm
  before_script:
    - apt-get update && apt-get install -y python3-pip
    - pip install -Ur src/requirements.txt
  script:
    - pytest -v src

build_image:
    stage: build
    image: docker:26.1.0
    services:
        - docker:26.1.0-dind
    variables:
        DOCKER_TLS_CERTDIR: "/certs"
    before_script:
        - docker login -u $DOCKER_USERNAME -p $DOCKER_TOKEN 
    script:
        - docker build -t $IMAGE_NAME:$IMAGE_TAG .
        - docker push $IMAGE_NAME:$IMAGE_TAG
    rules:
        - if: '$CI_COMMIT_TAG'

initialize_tf:
    stage: init-tf
    extends: .terraform:build
    rules:
        - if: '$CI_COMMIT_TAG'

deploy_tf:
    stage: deploy
    extends: .terraform:deploy
    dependencies:
        - initialize_tf
    environment:
        name: $TF_STATE_NAME
    rules:
        - if: '$CI_COMMIT_TAG'
```
Wir sehen, dass wir die Variable `IMAGE_TAG` auf `$CI_COMMIT_TAG` gesetzt haben. Das bedeutet, dass wir den Tag-Namen übernehmen, der gepsuht wurde. Wir haben auch die `rules` hinzugefügt, die besagt, dass die Stages nur ausgeführt werden, wenn ein Tag gepusht wird.

Zum Nachlesen:
https://medium.com/@helen_18602/gitlab-ci-cd-erstes-beispiel-feb903412bed 
