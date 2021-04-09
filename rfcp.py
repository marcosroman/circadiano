from utils import *
from odestuff import *
from netfunctions import *
import numpy as np
import os.path

args=get_args_forshift()

inifname=args.inifname
dirname=args.d
if(dirname=='\\'):
	dirname=os.path.dirname(inifname)
basename=os.path.basename(inifname)
N,netname,netinfo,netparams,netinst,K,s,omegainst,tequ,tmax,dt,eit,runinst,prntavgxy,prntallxy=getparamsfrominifile(basename)
shiftfactor=args.f
shiftinst=args.shiftinst

dirname=os.path.normpath(dirname) # por si lleva el '/' al final

#este string va a contener info de la red
netstring=netinfo+'__'+str(netinst)

#vamos definiendo los nombres de archivos donde guardamos (o de donde extraemos) los datos
runname="N"+str(int(N))+"-"+netstring+"-K"+str(float(K))+"-s"+str(float(s))+"__"+str(int(omegainst))+"-tequ"+str(float(tequ))+"-tmax"+str(float(tmax))+"-dt"+str(float(dt))+"-eit"+str(int(eit))+'__'+str(int(runinst))

# especificamos si imprimimos tambien 
if(prntallxy or prntavgxy):
	runname+='-'
	if(prntavgxy):
		runname+='-avgxy'
	if(prntallxy):
		runname+='-allxy'
runname+='--f'+str(shiftfactor)+'__'+str(shiftinst)

runfname=runname+".run" # archivo de corrida
nghbrfname=netstring+"-"+str(N)+".nghbr" # lista de vecinos (y para el caso de una red no dirigida, lo podemos tomar como la lista de conexiones entreantes o downstream, para cada oscilador)
omegafname=str(omegainst)+"-"+str(N)+".omega" # list of angular frequencies (careful with the precision here... load the whole thing)

# ahora tenemos que verificar si existe el archivo net y el archivo omega... y hacer, de acuerdo a ello, lo que corresponda
fullnghbrfname=dirname+'/'+nghbrfname
if (os.path.isfile(fullnghbrfname)):
    lnghbr=loadnghbr(fullnghbrfname)
    nghbrfileissaved=True
else:
    lnghbr=dnetfuncs[netname](N,netparams)
    nghbrfileissaved=False

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

#cargar condiciones iniciales...!
fullinitcfname=dirname+'/'+basename
finitc=open(fullinitcfname,"r")
ic=np.loadtxt(fullinitcfname)
#aprovecho que ya tengo N
for i in range(N):
    o[i].x=ic[i]*(1+shiftfactor*(2*random.random()-1))
    o[i].y=ic[N+i]*(1+shiftfactor*(2*random.random()-1))
#z=[np.zeros(2) for i in range(N)]

fullrunfname=dirname+'/'+runfname
if (os.path.isfile(fullrunfname)):
    print "El archivo "+fullrunfname+" ya existe. Salgo."
    exit()
if(not omegafileissaved):
    saveomega(lomega,fullomegafname)
if(not nghbrfileissaved):
    savenghbr(lnghbr,fullnghbrfname)

C=N*K/float(sum( [len(lnghbr[i]) for i in range(N)] ))

runfromcheckpoint(N,o,lnghbr,C,tequ,tmax,dt,eit,dirname+'/'+runfname,prntallxy,prntavgxy)
