
#    client_init = 0
#    client_stateless = 1
#    client_handshake = 2
#    client_1RTT = 3
#    client_0RTT = 4
#    client_close = 5
import pandas as pd

transition=[[0,1,1,0,1,0,0],[1,0,0,0,0,0,0],[0,0,1,1,0,0,0],[0,0,0,1,0,0,0],[0,1,0,0,1,0,0],[1,0,0,0,0,0,0],[0,0,0,0,0,0,0]] #currently the transition for Typ1 and type 0 is all zero.change it later
dict_picoquic = {'Type: 2': 0, 'Type: 3': 1, 'Type: 4': 2, 'Type: 6': 3,'Type: 5':4,'Type: 1':5,'Type: 0' :6} #(initial, retry, handshake, 1rtt, 0RTT,version,error)#type 1 version negotation
dict_ngtcp2 = {'0x7f':0,'0x7e':1,'0x7d':2,'S0':3} #(initial,retry,handshake,1RTT,0x7C=0-RTT)
print(transition)
out=""
result=open("result.html","w");

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
			if(transition[currstate][int(dict_picoquic[line[4:11]])] == 1):
				print("state changed")
				prevstate = currstate
				currstate = int(dict_picoquic[line[4:11]])
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
	if "Short" in var[5]:
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
		cLog = open("../"+implementation_name+"/quicly-client.log","r",errors='ignore')
	except FileNotFoundError:
		return
	lines=cLog.readlines()
	for line in lines:
		if line.find("handshake complete") > -1 :
			quicly_result["Handshake"]=1
		if line.find("switching version to") > -1 :
			quicly_result["Version Negotiation"]=1

def color_zero_red(val):
    color = 'red' if val.find(">0<") is not -1 else 'green'
    return 'background-color: %s' % color

def drawtable(implementation_name,result):
	d = {'picoquic' : pd.Series(picoquic_result), # index=['Version Negotiation','Handshake','Stateless Retry','1-RTT Stream Data']
		'ngtcp2' : pd.Series(ngtcp2_result),
		'quicly' : pd.Series(quicly_result)}
	df = pd.DataFrame(d)
	path = "../"+implementation_name
	df['picoquic']= df['picoquic'].apply(lambda x: '<a href='+path+'/picoquic-client.log>{0}</a>'.format(x))
	df['ngtcp2']= df['ngtcp2'].apply(lambda x: '<a href='+path+'/ngtcp2-client.log>{0}</a>'.format(x))
	df['quicly']= df['quicly'].apply(lambda x: '<a href='+path+'/quicly-client.log>{0}</a>'.format(x))
	styles = [ dict(selector="th", props=[("text-align", "center")]),dict(selector="", props=[("margin", "50px"),("display","inline-block")]) ]
	temp = df.style.applymap(color_zero_red).set_caption(implementation_name+' as Server').set_properties(**{'border': '2px solid black'}).set_table_styles(styles).render()	
	#print(temp)
	result.write(temp)
	#df.to_html('result.html')

def mainloop(result):
	number_of_implementations = 5
	implementation_name =["picoquic","quicly","mvfst","winquic","ngx_quic"]
	result.write("<h1 style='text-align:center;'>INTEROPERABILITY TEST MATRIX</h1>")
	for i in range(0,number_of_implementations):
		parsepicoquic(implementation_name[i])
		parsengtcp2(implementation_name[i])
		parsequicly(implementation_name[i])
		drawtable(implementation_name[i],result)
	print("End of parsing")

mainloop(result)
result.close()
