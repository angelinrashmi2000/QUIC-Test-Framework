#from enum import Enum
#class state(Enum):
#    client_init = 0
#    client_stateless = 1
#    client_handshake = 2
#    client_1RTT = 3
#    client_0RTT = 4
#    client_close = 5
import pandas as pd
import pdfkit as pdf
#from wkhtmltopdf import WKhtmlToPdf
currstate = 0
prevstate = 0
transition=[[0,1,1,0],[1,0,0,0],[0,0,1,1],[0,0,0,1]]
dict = {'Type: 2': 0, 'Type: 3': 1, 'Type: 4': 2, 'Type: 6': 3}
dict_ngtcp2 = {'0x7f':0,'0x7e':1,'0x7d':2,'S0':3}
print(transition)

out=""
def parse(line):
	var=line.split("(")
	var2=var[1].split(")")
	#print(var2[0])
	return var2[0]

cLog=open("/Users/Shared/Jenkins/Home/workspace/picoquic/picoquic-client.log","r");
result=open("result.txt","w");
result.write("Picoquic\n")                                                          
lines=cLog.readlines();
for line in lines:
	if(line[0:7] == "Sending"):
		print(out)
		out=""
		out =out + "Sending: "
	elif (line[0:9] == "Receiving"):
		print(out)
		out=""
		out =out + "Receiving: "
	elif(line.find("Type:") > -1):
		out = out + line[4:12]
		if(transition[currstate][int(dict[line[4:11]])] == 1):
			print("state changed")
			prevstate = currstate
			currstate = int(dict[line[4:11]])
			print(currstate)
			if(prevstate == 2 and currstate == 3):
				result.write("Handshake Complete\n")
				result.write("1-RTT Stream Data")
			if(prevstate == 0 and currstate == 1):
				result.write("Stateless Retry\n")
				
		else:
			print("error")
		k=parse(line)
		out = out+k
	elif(line[0:9] == "Processed"):
		print(parse(line))
def get5col(line):
	var =line.split(" ")
	if "0x7f" in var[5]:
		return "0x7f"
	if "0x7e" in var[5]:
		return "0x7e"
	if "0x7d" in var[5]:
		return "0x7d"
	if "S0" in var[5]:
		return "S0"

def parsengtcp2():
	cLog = open("/Users/Shared/Jenkins/Home/workspace/picoquic/ngtcp2-client.log","r");
	#cLog = open("/Users/Rashmi/Documents/workspace/sample/ngtcp2/ngtcp2-client.log","r");
	result.write("Ngtcp2\n")
	lines=cLog.readlines()
	currstate = 0
	prevstate = 0
	prevpkt = -1
	currpkt = 0
	for line in lines:
		if(line.count(" ") > 2 and line.split(" ")[2].find("frm") > -1):
			if(transition[currstate][int(dict_ngtcp2[get5col(line)])] == 1):
				print("state changed")
				prevstate = currstate
				currstate = int(dict_ngtcp2[get5col(line)])
				print(currstate)
				if(prevstate == 2 and currstate == 3):
					result.write("Handshake Complete\n")
					result.write("1-RTT Stream Data")
				if(prevstate == 0 and currstate == 1):
					result.write("Stateless Retry\n")
					
			else:
				print("error")


def drawtable():
	d = {'Handshake' : pd.Series([1,0],index=['picoquic','ngtcp2']),
		'Statless Retry' :pd.Series([0,1],index=['picoquic','ngtcp2'])}
	df = pd.DataFrame(d)
	df.to_html('result.html')
	file = 'result.pdf'
	#pdf.from_file('result.html', file)

parsengtcp2()
drawtable()

result.close()
