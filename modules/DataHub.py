# HTTP Get
# HTTP Put
# HTTP Post
# reference https://stackoverflow.com/questions/48819698/importerror-no-module-named-httplib-pip-install-httplib2-did-not-solve?noredirect=1&lq=1
import httplib2
import json
import re


#initial
http = httplib2.Http()
server = 'https://raw.githubusercontent.com/kmi-robots/sciroc-datahub-specs/master/swagger.json'#'https://api.pp.mksmart.org/sciroc-competition/'#'https://raw.githubusercontent.com/kmi-robots/sciroc-datahub-specs/master/swagger.json'
accessKey = 'd22ec71d-af83-4cd6-847c-ea5031870d9b'
password ='bathdrones'


connection =  http.request(server)[1]
print(connection.decode())

stripped = re.sub('<[^<]+?>', '', connection.decode())
print(stripped)

#decoded  =  dumps()
