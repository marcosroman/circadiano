import numpy as np
import random
from sys import argv

'''
Copio lo que dice el paper de watts y strogatz. No si si lo estuve haciendo muy bien a esto antes, en mi codigo en c. quizas deberia verificar, especialmente porque para p=0 y p=0.05 los resultados que tenia eran muy similares D:

"We choose a vertex and the edge that connects it to its nearest neighbour in a clockwise sense. With probability p, we reconnect this edge to a vertex chosen uniformly at random over the entire ring, with duplicate edges forbidden; other- wise we leave the edge in place. We repeat this process by moving clockwise around the ring, considering each vertex in turn until one lap is completed. Next, we consider the edges that connect vertices to their second-nearest neighbours clockwise. As before, we randomly rewire each of these edges with probability p, and continue this process, circulating around the ring and proceeding outward to more distant neighbours after each lap, until each edge in the original lattice has been considered once."
'''

def lneighbors2amatrix(lneighbors):
	m=np.zeros([N,N])
	for i in range(N):
		for j in lneighbors[i]:
			m[(i,j)]=1
	
	return m

# lo siguiente es escribir algun algoritmo runge kutta... luego lo que quedaria seria iniciar un conjunto de osciladores, conectarlos
class hopfoscillator:
	#def __init__(self,sigma=0.1,a2=1,gamma=1,mu=1,x=np.random.random(),y=np.random.random()):
	# quiero ver que onda si pongo mu=0
	def __init__(self,sigma=0.1,a2=1,gamma=1,mu=0,x=np.random.random(),y=np.random.random()):
		self.omega=random.gauss(mu=mu,sigma=sigma)
		self.a2=a2
		self.gamma=gamma
		self.x=random.random()*2.-1.
		self.y=random.random()*2.-1.

import argparse

def get_args():
	parser=argparse.ArgumentParser()
	parser.add_argument('-N',type=int,required=True,help="Number of oscillators")
	parser.add_argument('-net',type=str,required=True,help="<Network Name>(<arguments>)")
	#parser.add_argument('-q',type=int,help="Nq is the initial number of links",default=2)
	#parser.add_argument('-p',type=float,required=True,help="Rewiring probability")
	parser.add_argument('-K',type=float,required=True,help="(constant) Coupling \"Strength\"")
	parser.add_argument('-s','-sigma',type=float,required=True,help="Angular frequency distribution spead (in our case, gaussian std)")
	parser.add_argument('-netinst','-in',type=int,default=0,help="Instance of network with given parameters (e.g., -netinst=0 for q=2 and p=0.01 is saved as ws_2_0.01-32.net)")
	parser.add_argument('-omegainst','-io',type=int,default=0,help="Instance of list of angular frequencies. Saved as instance-N.omega")
	parser.add_argument('-runinst','-ir',type=int,default=0,help="Instance of run")
	parser.add_argument('-tequ',type=float,default=100,help="Equilibration time")
	parser.add_argument('-tmax',type=float,default=100)
	parser.add_argument('-dt',type=float,default=0.0625)
	parser.add_argument('-eit',type=int,default=1,help="Print/save every \'eit\' time step")
	parser.add_argument('-printallxy','-xy',action='store_true',help="Print x_i,y_i for every oscillator")
	parser.add_argument('-printavgxy','-avgxy',action='store_true',help="Print avgx,avgy")
	parser.add_argument('dirname')
	return parser.parse_args()

def get_args_forshift():
	parser=argparse.ArgumentParser()
	#parser.add_argument('-printallxy','-xy',action='store_true',help="Print x_i,y_i for every oscillator")
	#parser.add_argument('-printavgxy','-avgxy',action='store_true',help="Print avgx,avgy")
	parser.add_argument('-d','-dirname',type=str,default='\\')#pongo eso de default, asi dsp si eso es lo que queda, el dirname sera el os.path.dirname(inifname)
	parser.add_argument('-f','-shiftfactor',type=float,required=True,help="random shift factor")
	parser.add_argument('-shiftinst','-if',type=int,default=0,help="Instance of shift")
	parser.add_argument('inifname')

	return parser.parse_args()

'''
def get_args_forshift():
	parser=argparse.ArgumentParser()
	parser.add_argument('-N',type=int,required=True,help="Number of oscillators")
	parser.add_argument('-net',type=str,required=True,help="<Network Name>(<arguments>)")
	parser.add_argument('-K',type=float,required=True,help="(constant) Coupling \"Strength\"")
	parser.add_argument('-s','-sigma',type=float,required=True,help="Angular frequency distribution spead (in our case, gaussian std)")
	parser.add_argument('-netinst','-in',type=int,default=0,help="Instance of network with given parameters (e.g., -netinst=0 for q=2 and p=0.01 is saved as ws_2_0.01-32.net)")
	parser.add_argument('-omegainst','-io',type=int,default=0,help="Instance of list of angular frequencies. Saved as instance-N.omega")
	parser.add_argument('-runinst','-ir',type=int,default=0,help="Instance of run")
	parser.add_argument('-tequ',type=float,default=50,help="Equilibration time")
	parser.add_argument('-tmax',type=float,default=100)
	parser.add_argument('-dt',type=float,default=0.0625)
	parser.add_argument('-eit',type=int,default=1,help="Print/save every \'eit\' time step")
	parser.add_argument('-printallxy',action='store_true',help="Print x_i,y_i for every oscillator")
	parser.add_argument('-printavgxy',action='store_true',help="Print avgx,avgy")
	parser.add_argument('dirname')
	parser.add_argument('-f','-shiftfactor',type=float,required=True,help="random shift factor")
	parser.add_argument('-shiftinst','-if',type=int,default=0,help="Instance of shift")
	parser.add_argument('initcfname')

	return parser.parse_args()
'''

def loadomega(fullomegafname):
	lomega=[]
	fin=open(fullomegafname,"r")

	keepreading=True
	while(keepreading==True):
		line=fin.readline()[:-1]
		if (line==''):
			keepreading=False
		else:
			lomega.append(float(line))
	fin.close()

	return lomega

def saveomega(lomega,fullomegafname):
	fout=open(fullomegafname,"w")		
	for omega in lomega:
		fout.write("%0.64e\n" % omega)
	fout.close()

def loadnghbr(fullnghbrfname):
	fin=open(fullnghbrfname,"r")
	lnghbors=[]

	keepreading=True
	while(keepreading==True):
		line=fin.readline()[:-1]
		if (line==''):
			keepreading=False
		else:
			lnghbors.append([])
			splitline=line.split(" ")
			for e in splitline:
				lnghbors[-1].append(int(e))
	fin.close()
	
	return lnghbors

def savenghbr(lnghbors,fullnghbrfname):
	fout=open(fullnghbrfname,"w")
	for incominglist in lnghbors:
		for incomingnode in incominglist[:-1]:
			fout.write(str(incomingnode)+" ")
		fout.write(str(incominglist[-1])+"\n")
	fout.close()

def getnetnameandparams(netargs):
	netname=netargs.split('(')[0]
	netparams=netargs.split('(')[1][:-1].split(',')
	return netname,netparams

# get params from initfile (.ini extension)
def getparamsfrominifile(fname):
	if not '.ini' in fname:
		print "No es un archivo .ini"
		quit()

	printallxy=('allxy' in fname)
	printavgxy=('avgxy' in fname)

	if (printallxy or printavgxy):
		f0=fname.split('--')[0]
	else:
		f0=fname[:-4]

	splitbasename=f0.split('-')

	N=int(splitbasename[0][1:])
	K=float(splitbasename[2][1:])
	tequ=float(splitbasename[4][4:])
	tmax=float(splitbasename[5][4:])
	dt=float(splitbasename[6][2:])
	splitnet=splitbasename[1].split('__')
	netinst=int(splitnet[1])
	netinfo=splitnet[0]
	if('_') in netinfo:
			netname=netinfo.split('_')[0]
			netparams=netinfo.split('_')[1:]
	else:
			netname=netinfo
			netparams=[]
	splitsigma=splitbasename[3].split('__')
	omegainst=int(splitsigma[1])
	s=float(splitsigma[0][1:])
	spliteit=splitbasename[-1].split('__')
	runinst=int(spliteit[1])
	eit=int(spliteit[0][3:])

	return N,netname,netinfo,netparams,netinst,K,s,omegainst,tequ,tmax,dt,eit,runinst,printavgxy,printallxy

# get params from any file with .xxx extension
def getparamsfromanyfile(fname):
	printallxy=('allxy' in fname)
	printavgxy=('avgxy' in fname)

	if (printallxy or printavgxy):
		f0=fname.split('--')[0]
	else:
		f0=fname[:-4]

	splitbasename=f0.split('-')

	N=int(splitbasename[0][1:])
	K=float(splitbasename[2][1:])
	tequ=float(splitbasename[4][4:])
	tmax=float(splitbasename[5][4:])
	dt=float(splitbasename[6][2:])
	splitnet=splitbasename[1].split('__')
	netinst=int(splitnet[1])
	netinfo=splitnet[0]
	if('_') in netinfo:
			netname=netinfo.split('_')[0]
			netparams=netinfo.split('_')[1:]
	else:
			netname=netinfo
			netparams=[]
	splitsigma=splitbasename[3].split('__')
	omegainst=int(splitsigma[1])
	s=float(splitsigma[0][1:])
	spliteit=splitbasename[-1].split('__')
	runinst=int(spliteit[1])
	eit=int(spliteit[0][3:])

	return N,netname,netinfo,netparams,netinst,K,s,omegainst,tequ,tmax,dt,eit,runinst,printavgxy,printallxy

# esta funcion sirve para pasar datos guardados en un array a una matriz (o sea, serian datos que corresponden a una grilla)
def array2matrix(array):
	N=len(array)
	sqrn=np.sqrt(N)
	if not sqrn.is_integer():
		print "El numero de elementos del array no es cuadrado."
	else:
		sqrn=int(sqrn)

	matrix=np.zeros([sqrn,sqrn])

	for i in range(N):
		iy=i%sqrn
		ix=(i-iy)/sqrn
		matrix[ix,iy]=array[i]
	
	return matrix
