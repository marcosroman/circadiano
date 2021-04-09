import random
from math import fmod,sqrt

def ws_netf(N,params):
	q,p=params
	q=int(q)
	p=float(p)
	lneighbors=[[] for i in range(N)]

	for i in range(N):
		for iq in range(q):
			lneighbors[i].append((i+iq+1)%N)
			lneighbors[i].append((i-iq-1)%N)

	if (p>0):
		# (seguimos las instrucciones del paper, para reconectar...)
		# para cada uno de los q links por nodo...
		for iq in range(q):
			# vamos nodo por nodo...
			for i in range(N):
				# entonces lo que vamos a ver ahora es si cambiamos o no su conexion con el nodo (i+iq+1)%N
				if (random.random()<=p):
					lnotneighborsofi=range(N)
					lnotneighborsofi.remove(i) # (no hay autoconexiones)
					for j in lneighbors[i]:
						lnotneighborsofi.remove(j)
					newnode=random.choice(lnotneighborsofi)
					
					# entonces desconectamos a i del nodo (i+iq+1)%N...
					lneighbors[i].remove((i+iq+1)%N)
					lneighbors[(i+iq+1)%N].remove(i)
					# ...y lo conectamos con el nodo newnode
					lneighbors[i].append(newnode)
					lneighbors[newnode].append(i)
	
	# me di cuenta de que cuando elijo q=N/2 (como para hacer all to all) se repite el ultimo nodo.. entonces hacemos este quickndirty fix
	for i in range(len(lneighbors)):
		lneighbors[i]=list(set(lneighbors[i]))

	return lneighbors

def ws2d_netf(N,params):
	rmax,p=params
	rmax=float(rmax)
	p=float(p)
	rmax2=rmax**2

	if not sqrt(N).is_integer():
		print "sqrt(N) no es entero, no se puede construir red ws2d"
		quit()
	
	sqrn=int(sqrt(N))
	pos=[]
	for i in range(N):
		iy=i%sqrn
		ix=(i-iy)/sqrn
		pos.append([ix,iy])
	
	lneighbors=[[] for i in range(N)]
	for i in range(N):
		for j in range(N)[i+1:]:
			#recordar las condiciones periodicas de contorno para calcular la distancia!
			distx=abs(pos[i][0]-pos[j][0])
			disty=abs(pos[i][1]-pos[j][1])
			distx=min(distx,abs(distx-sqrn))
			disty=min(disty,abs(disty-sqrn))
			#distx=fmod(pos[i][0]-pos[j][0],sqrn)
			#disty=fmod(pos[i][1]-pos[j][1],sqrn)
			if( distx**2+disty**2 <= rmax2 ):
				lneighbors[i].append(j)
				lneighbors[j].append(i)

	#luego de conectar cosas, calculamos q en funcion de rmax, ya que vamos a pasar q veces por cada nodo para reconectar un link suyo... 2*q=<k>
	#reconectar!
	if (p>0):
		# siendo este el caso bidimensional, tengo que pensar un poco mejor como hacer la reconexion; antes, para el caso 1d, lo que hacia era -dado un i y un iq- desconectar del nodo i el nodo (i+iq+1)%N y luego reconectar aleatoriamente con otro... entonces, para hacer algo similar a eso, ahora tengo que considerar, dado un nodo i, solo los nodos que son mayores para reconectar (y tengo que tener cuidado ahi usando modulo o algo asi... ya que para el nodo N-1, el nodo 0 es 'mayor' o esta 'adelante en la lista', pero si no tenemos cuidado esto no va a ser considerado. entonces...
		q=len(lneighbors[0])/2
		lnghbrsmayores=[]
		for i in range(N):
			lnghbrsmayores.append(list(lneighbors[i]))
		for i in range(N):
			for j in lneighbors[i]:
				dy=pos[j][1]-pos[i][1]
				dx=pos[j][0]-pos[i][0]
				if(abs(dx)>=float(sqrn)/2.):
					if(dx>0):
						dx-=(sqrn)
					else:
						dx+=(sqrn)
				if(abs(dy)>=float(sqrn)/2.):
					if(dy>0):
						dy-=(sqrn)
					else:
						dy+=(sqrn)
				nsteps=dx+dy
				if (nsteps<0 or (nsteps==0 and dy<0)):
					lnghbrsmayores[i].remove(j)
		# de esta forma, para cada nodo i, me quedo con los nodos a los que esta conectado de un lado de la diagonal con pendiente -1 que pasa sobre el mismo (o sea, divido el plano entre dos con esa diagonal y solo me quedo con los nodos de arriba, los 'mayores', de forma similar a ws1d)
			
		# (seguimos las instrucciones del paper, para reconectar...)
		# para cada uno de los q links por nodo...
		for iq in range(q):
			# vamos nodo por nodo...
			for i in range(N):
				# entonces lo que vamos a ver ahora es si cambiamos o no su conexion con el nodo (i+iq+1)%N
				if (random.random()<=p):
					lnotneighborsofi=range(N)
					lnotneighborsofi.remove(i) # (no hay autoconexiones)
					for j in lneighbors[i]:
						lnotneighborsofi.remove(j)
					newnode=random.choice(lnotneighborsofi)
					
					# entonces desconectamos a i del nodo lnghbrsmayores[i][iq]
					nodetounplug=lnghbrsmayores[i][iq]
					lneighbors[i].remove(nodetounplug)
					lneighbors[nodetounplug].remove(i)
					# ...y lo conectamos con el nodo newnode
					lneighbors[i].append(newnode)
					lneighbors[newnode].append(i)
	
	for i in range(len(lneighbors)):
		lneighbors[i]=list(set(lneighbors[i]))

	return lneighbors

# watts strogatz 2d but without periodic boundary conditions
def ws2dnpbc_netf(N,params):
	rmax,p=params
	rmax=float(rmax)
	p=float(p)
	rmax2=rmax**2

	if not sqrt(N).is_integer():
		print "sqrt(N) no es entero, no se puede construir red ws2d"
		quit()
	
	sqrn=int(sqrt(N))
	pos=[]
	for i in range(N):
		iy=i%sqrn
		ix=(i-iy)/sqrn
		pos.append([ix,iy])
	
	lneighbors=[[] for i in range(N)]
	for i in range(N):
		for j in range(N)[i+1:]:
			# como ahora hago sin condiciones periodicas de contorno, lo que queda es simplemente comentar las siguientes terceras y cuartas lineas... el resto queda todo igual...
			distx=abs(pos[i][0]-pos[j][0])
			disty=abs(pos[i][1]-pos[j][1])
			#distx=min(distx,abs(distx-sqrn))
			#disty=min(disty,abs(disty-sqrn))
			#distx=fmod(pos[i][0]-pos[j][0],sqrn)
			#disty=fmod(pos[i][1]-pos[j][1],sqrn)
			if( distx**2+disty**2 <= rmax2 ):
				lneighbors[i].append(j)
				lneighbors[j].append(i)

	#luego de conectar cosas, calculamos q en funcion de rmax, ya que vamos a pasar q veces por cada nodo para reconectar un link suyo... 2*q=<k>
	#reconectar!
	if (p>0):
		# lo de la reconeccion se hace igual que en el caso 2D with pbc
		q=len(lneighbors[0])/2
		lnghbrsmayores=[]
		for i in range(N):
			lnghbrsmayores.append(list(lneighbors[i]))
		for i in range(N):
			for j in lneighbors[i]:
				dy=pos[j][1]-pos[i][1]
				dx=pos[j][0]-pos[i][0]
				if(abs(dx)>=float(sqrn)/2.):
					if(dx>0):
						dx-=(sqrn)
					else:
						dx+=(sqrn)
				if(abs(dy)>=float(sqrn)/2.):
					if(dy>0):
						dy-=(sqrn)
					else:
						dy+=(sqrn)
				nsteps=dx+dy
				if (nsteps<0 or (nsteps==0 and dy<0)):
					lnghbrsmayores[i].remove(j)
		# de esta forma, para cada nodo i, me quedo con los nodos a los que esta conectado de un lado de la diagonal con pendiente -1 que pasa sobre el mismo (o sea, divido el plano entre dos con esa diagonal y solo me quedo con los nodos de arriba, los 'mayores', de forma similar a ws1d)
			
		# (seguimos las instrucciones del paper, para reconectar...)
		# para cada uno de los q links por nodo...
		for iq in range(q):
			# vamos nodo por nodo...
			for i in range(N):
				# entonces lo que vamos a ver ahora es si cambiamos o no su conexion con el nodo (i+iq+1)%N
				if (random.random()<=p):
					lnotneighborsofi=range(N)
					lnotneighborsofi.remove(i) # (no hay autoconexiones)
					for j in lneighbors[i]:
						lnotneighborsofi.remove(j)
					newnode=random.choice(lnotneighborsofi)
					
					# entonces desconectamos a i del nodo lnghbrsmayores[i][iq]
					nodetounplug=lnghbrsmayores[i][iq]
					lneighbors[i].remove(nodetounplug)
					lneighbors[nodetounplug].remove(i)
					# ...y lo conectamos con el nodo newnode
					lneighbors[i].append(newnode)
					lneighbors[newnode].append(i)
	
	for i in range(len(lneighbors)):
		lneighbors[i]=list(set(lneighbors[i]))

	return lneighbors

def alltoall_netf(N,params):
	lneighbors=[range(N) for i in range(N)]
	for i in range(N):
		lneighbors[i].remove(i)
	return lneighbors

# erdos renyi (aka random)
def er_netf(N,params):
	p=params[0]
	p=float(p)
	lneighbors=[[] for i in range(N)]
	
	for i in xrange(N):
		for j in xrange(i+1,N):
			r=random.random()
			if (r<=p):
				lneighbors[i].append(j)
				lneighbors[j].append(i)
	
	return lneighbors

dnetparams={'ws':['q','p'],'ws2d':['rmax','p'],'ws2dnpbc':['rmax','p'],'alltoall':[],'er':['r']}
dnetfuncs={'ws':ws_netf,'ws2d':ws2d_netf,'ws2dnpbc':ws2dnpbc_netf,'alltoall':alltoall_netf,'er':er_netf} 
