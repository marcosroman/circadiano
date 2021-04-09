# este script genera redes de forma independiente, pero usando las mismas funciones que estan en run.py (usando las funciones de utils.py y netfuncs.py) 

from utils import saveomega
import random
import os.path
import argparse

muomega=0 # el promedio de la dist gaussiana para omega

def get_net_args():
	parser=argparse.ArgumentParser()
	parser.add_argument('-N',type=int,required=True,help="Number of oscillators")
	parser.add_argument('-s','-sigma',type=float,required=True,help="Angular frequency distribution spead (in our case, gaussian std)")
	parser.add_argument('-omegainst','-io',type=int,default=0,help="Instance of list of angular frequencies. Saved as instance-N.omega")
	parser.add_argument('dirname')
	return parser.parse_args()

args=get_net_args()

N=args.N
s=args.s
omegainst=args.omegainst
dirname=args.dirname
dirname=os.path.normpath(dirname) # por si lleva el '/' al final

omegafname=str(omegainst)+"-"+str(N)+"_"+str(s)+".omega" # list of angular frequencies (careful with the precision here... load the whole thing)
fullomegafname=dirname+'/'+omegafname
if (os.path.isfile(fullomegafname)):
	print "Ya existe",fullomegafname
	quit()
else:
	lomega=[]
	for i in range(N):
		lomega.append(random.gauss(mu=muomega,sigma=s))
	
	# sin importar el muomega, voy a forzar que tenga promedio cero esto
	avgomega=sum(lomega)/float(len(lomega))
	for i in xrange(N):
		lomega[i]-=avgomega

	saveomega(lomega,fullomegafname)


