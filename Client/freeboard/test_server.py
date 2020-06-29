import requests
import json
ip = "127.0.0.1"
port= 8080

params = {"widgets": [
				{
					"type": "ciao",
					"settings": {
						"value": [
							"datasources[\"gas\"][\"feeds\"][0][\"field1\"]"
						]
					}
				}
			]}

stringa = json.dumps(params)
#res = requests.post("http://"+ip+":"+str(port)+'/saveDashboard?json_string='+stringa)
res = requests.get("http://"+ip+":"+str(port)+'/dashboard.json')

print(res.status_code)