import requests

ip = "127.0.0.1"
port= 8080

#res = requests.post("http://"+ip+":"+str(port)+'/saveDashboard?json_string=dashboard.json')
res = requests.get("http://"+ip+":"+str(port))

print(res.status_code)