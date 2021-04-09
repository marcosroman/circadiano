from utils import *
from odestuff import *
from netfunctions import *
import os.path # para verificar si existe un archivo

args=get_args()

N=args.N
netargs=args.net
netinst,omegainst,runinst=args.netinst,args.omegainst,args.runinst
K,s=args.K,args.s
tequ,tmax,dt,eit=args.tequ,args.tmax,args.dt,args.eit
prntallxy,prntavgxy=args.printallxy,args.printavgxy

if( (netargs!='?') and ('(' in netargs) and (')' in netargs) ):
	netname,netparams=getnetnameandparams(netargs)
else:
	# print network usage (listando redes, con sus respetivos parametros)
	quit()

dirname=args.dirname
dirname=os.path.normpath(dirname) # por si lleva el '/' al final

netstring=netname
#este string va a contener info de la red
if(netparams[0]!=''):
	for np in netparams:
		netstring+='_'+np
netstring+='__'+str(netinst)

#vamos definiendo los nombres de archivos donde guardamos (o de donde extraemos) los datos
runname="N"+str(int(N))+"-"+netstring+"-K"+str(float(K))+"-s"+str(float(s))+"__"+str(int(omegainst))+"-tequ"+str(float(tequ))+"-tmax"+str(float(tmax))+"-dt"+str(float(dt))+"-eit"+str(int(eit))+'__'+str(int(runinst))

# especificamos si imprimimos tambien 
if(prntallxy or prntavgxy):
	runname+='-'
	if(prntavgxy):
		runname+='-avgxy'
	if(prntallxy):
		runname+='-allxy'

runfname=runname+".runx" # archivo de corrida
nghbrfname=netstring+"-"+str(N)+".nghbr" # lista de vecinos (y para el caso de una red no dirigida, lo podemos tomar como la lista de conexiones entreantes o downstream, para cada oscilador)
omegafname=str(omegainst)+"-"+str(N)+"_"+str(s)+".omega" # list of angular frequencies (careful with the precision here... load the whole thing)
initcfname=runname+".ini"

# continuamos solo en caso de que no exista el archivo run (podria tambien hacerlo con initc, pero creo que con esto basta)
fullrunfname=dirname+'/'+runfname
if (os.path.exists(fullrunfname)): #antes usaba la funcion isfile(), pero eso retorna False si se trata de un softlink. exists() se supone que no
	print "El archivo "+fullrunfname+" ya existe. Salgo."
	exit()

# ahora tenemos que verificar si existe el archivo nghbr... y el archivo omega... y hacer, de acuerdo a ello, lo que corresponda
fullnghbrfname=dirname+'/'+nghbrfname
if (os.path.exists(fullnghbrfname)):
	lnghbr=loadnghbr(fullnghbrfname)
	#nghbrfileissaved=True
else:
	lnghbr=dnetfuncs[netname](N,netparams)
	#nghbrfileissaved=False
	#if(not nghbrfileissaved):
	savenghbr(lnghbr,fullnghbrfname)

# creamos los osciladores ya...
o=[hopfoscillator(sigma=s) for i in range(N)]

# y lo mismo para el archivo de omega (vemos si esta o no)
fullomegafname=dirname+'/'+omegafname
if (os.path.isfile(fullomegafname)):
	lomega=loadomega(fullomegafname)
	for i in range(N):
		o[i].omega=lomega[i]
	omegafileissaved=True
else:
	lomega=[]
	for i in range(N):
		lomega.append(o[i].omega)
	omegafileissaved=False
if(not omegafileissaved):
	saveomega(lomega,fullomegafname)

C=N*K/float(sum( [len(lnghbr[i]) for i in range(N)] ))
run(N,o,lnghbr,C,tequ,tmax,dt,eit,dirname+'/'+runfname,dirname+'/'+initcfname,prntallxy,prntavgxy)
