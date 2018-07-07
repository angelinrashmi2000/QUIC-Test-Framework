
#    client_init = 0
#    client_stateless = 1
#    client_handshake = 2
#    client_1RTT = 3
#    client_0RTT = 4
#    client_close = 5
import pandas as pd
import pdfkit as pdf
#from wkhtmltopdf import WKhtmlToPdf


transition=[[0,1,1,0,1],[1,0,0,0,0],[0,0,1,1,0],[0,0,0,1,0],[0,1,0,0,1]]
dict = {'Type: 2': 0, 'Type: 3': 1, 'Type: 4': 2, 'Type: 6': 3,'Type: 5':4}
dict_ngtcp2 = {'0x7f':0,'0x7e':1,'0x7d':2,'S0':3}
print(transition)
out=""

picoquic_result ={"Version Negotiation":0,"Handshake":0,"Stateless Retry":0,"1-RTT":0}
ngtcp2_result ={"Version Negotiation":0,"Handshake":0,"Stateless Retry":0,"1-RTT":0}
quicly_result ={"Version Negotiation":0,"Handshake":0,"Stateless Retry":0,"1-RTT":0}

def parse(line):
	var=line.split("(")
	var2=var[1].split(")")
	return var2[0]

def parsepicoquic(implementation_name):
	out=""
	currstate = 0
	prevstate = 0
	picoquic_result["Version Negotiation"] =0
	picoquic_result["Handshake"]=0
	picoquic_result["Stateless Retry"]=0
	picoquic_result["1-RTT"]=0
	try:
		cLog=open("../"+implementation_name+"/picoquic-client.log","r"); 
	except FileNotFoundError:
		return                                                       
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
					picoquic_result["Handshake"] =1
					picoquic_result["1-RTT"]=1
				if(prevstate == 0 and currstate == 1):
					picoquic_result["Stateless Retry"] =1
					
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

def parsengtcp2(implementation_name):
	try:
		cLog = open("../"+implementation_name+"/ngtcp2-client.log","r");
	except FileNotFoundError:
		return
	lines=cLog.readlines()
	ngtcp2_result["Version Negotiation"] =0
	ngtcp2_result["Handshake"]=0
	ngtcp2_result["Stateless Retry"]=0
	ngtcp2_result["1-RTT"]=0
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
					ngtcp2_result["Handshake"]=1
					ngtcp2_result["1-RTT"]=1
				if(prevstate == 0 and currstate == 1):
					ngtcp2_result["Stateless Retry"]=1
			else:
				print("error")

def parsequicly(implementation_name):
	quicly_result["Version Negotiation"] =0
	quicly_result["Handshake"]=0
	quicly_result["Stateless Retry"]=0
	quicly_result["1-RTT"]=0
	try:
		cLog = open("../"+implementation_name+"/quicly-client.log","r")
	except FileNotFoundError:
		lines=cLog.readlines()
		for line in lines:
			if line.find("handshake complete") >= -1 :
				quicly_result["Handshake"]=1

def color_zero_red(val):
    color = 'red' if val is 0 else 'green'
    return 'background-color: %s' % color

def drawtable(implementation_name):
	d = {'Picoquic' : pd.Series(picoquic_result),#,index=['Version Negotiation','Handshake','Stateless Retry','1-RTT Stream Data']),
		'ngtcp2' : pd.Series(ngtcp2_result),
		'quicly' : pd.Series(quicly_result)}
	df = pd.DataFrame(d)
	temp = df.style.applymap(color_zero_red).set_caption(implementation_name+' as Server').render()
	print(temp)
	result=open("result.html","w");
	result.write(temp)
	result.close()
	#df.to_html('result.html')

def mainloop():
	number_of_implementations = 2
	implementation_name =["picoquic","quicly","mvfst","winquic","ngx_quic"]
	for i in range(0,number_of_implementations):
		parsepicoquic(implementation_name[i])
		parsengtcp2(implementation_name[i])
		parsequicly(implementation_name[i])
		drawtable(implementation_name[i])
	print("End of parsing")

mainloop()


