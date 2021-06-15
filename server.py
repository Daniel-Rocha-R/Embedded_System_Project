from flask import Flask
from flask import render_template
import json

app = Flask(__name__)

@app.route('/a')
def root():
    return render_template('table.html')
    
@app.route('/hello.html')
def hello():
	return 'Hello, World!'

	
@app.route('/get_data.json')
def get_data():
	response = {"data": []}
	with open ('datos.csv') as fin:
		data = fin.readline()
		text_td=" "
		#print data
		for line in fin:
			RPM,POWER,DATE_TIME = line.rstrip('\n').split(",")
			response['data'].append([RPM, POWER, DATE_TIME])
			
		jsonStr = json.dumps(response)
		return jsonStr
		


if __name__ == '__main__':
	app.run(host="0.0.0.0")
