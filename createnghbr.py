# este script genera redes de forma independiente, pero usando las mismas funciones que estan en run.py (usando las funciones de utils.py y netfuncs.py) 

from utils import getnetnameandparams, savenghbr
from netfunctions import *
import os.path
import argparse

def get_net_args():
	parser=argparse.ArgumentParser()
	parser.add_argument('-N',type=int,required=True,help="Number of oscillators")
	parser.add_argument('-net',type=str,required=True,help="<Network Name>(<arguments>)")
	parser.add_argument('-netinst','-in',type=int,default=0,help="Instance of network with given parameters (e.g., -netinst=0 for q=2 and p=0.01 is saved as ws_2_0.01-32.net)")
	parser.add_argument('dirname')
	return parser.parse_args()

args=get_net_args()

N=args.N
netargs=args.net
netinst=args.netinst

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

nghbrfname=netstring+"-"+str(N)+".nghbr"

# ahora tenemos que verificar si existe el archivo nghbr... si no existe, creamos la red y la guardamos
fullnghbrfname=dirname+'/'+nghbrfname
if (os.path.exists(fullnghbrfname)):
	#lnghbr=loadnghbr(fullnghbrfname)
	print "Ya existe",fullnghbrfname
else:
	lnghbr=dnetfuncs[netname](N,netparams)
	savenghbr(lnghbr,fullnghbrfname)
