from libc.stdlib cimport malloc, free
from libc.math cimport sqrt
from os.path import exists

cdef void dzdt(double t, int N, double C, double p[], int a[], double z[], double dz[]):
	cdef double x
	cdef double y
	cdef double r2
	cdef double omega
	cdef double c[2]
	cdef int i
	cdef int j
	for i from 0<=i<N:
		x=z[2*i+0]
		y=z[2*i+1]
		c[0]=0.
		c[1]=0.
		#for j in xrange(N):
		for j from 0<=j<N:
			if (a[i*N+j]==1):
				c[0]+=(z[2*j+0]-z[2*i+0])
				c[1]+=(z[2*j+1]-z[2*i+1])
		c[0]*=C
		c[1]*=C
		r2=x*x+y*y
		omega=p[3*i+0]
		dz[2*i+0]=-x*(r2-1.)-omega*y+c[0];
		dz[2*i+1]=-y*(r2-1.)+omega*x+c[1];

cdef void rk4(double z[], double dz[], int N, int n, double C, double t, double h, double p[], int a[], double zout[]):
	cdef int i
	cdef double th
	cdef double hh
	cdef double h6
	cdef double *dzm
	cdef double *dzt
	cdef double *zt
  
	dzm=<double *>malloc(sizeof(double)*(n));
	dzt=<double *>malloc(sizeof(double)*(n));
	zt=<double *>malloc(sizeof(double)*(n));
	
	hh=h*0.5;
	h6=h/6.0;
	th=t+hh;
  
	for i in xrange(n):
		zt[i]=z[i]+hh*dz[i];
	dzdt(th,N,C,p,a,zt,dzt);
	for i in xrange(n):
		zt[i]=z[i]+hh*dzt[i];
	dzdt(th,N,C,p,a,zt,dzm);
	for i in xrange(n):
		zt[i]=z[i]+h*dzm[i];
	#for i in xrange(n):
		dzm[i] += dzt[i]
	dzdt(t+h,N,C,p,a,zt,dzt);
	for i in xrange(n):
		zout[i]=z[i]+h6*(dz[i]+dzt[i]+2.0*dzm[i])
	free(zt);
	free(dzt);
	free(dzm);

# 'o' son los osciladores ya inicializados...
# ok... toda esta parte del codigo funciona ya, pero tengo que pasarle todos los parametros necesarios para lograr que todo funcione como quiero, que pueda replicar el comportamiento del codigo anterior (en python puro) pero con mayor velocidad
# los parametros necesarios son entonces... (recordar agregar lo del flag para que imprima todos los x_i si hace falta...)
#   : N,o,lnghbr, K, f (el archivo donde se guardaria todo...), tequ (tiempo de equilibracion), cadait (cada cuantos pasos guardo realmente... sera necesario esto? porque es medio peligroso que haya aliasing. en fin, lo dejaremos para despues)
#   : q, dt tmax, finitial (el archivo donde se guardan las condiciones iniciales...)
def run(N,o,lnghbr,pC,ptequ,ptmax,pdt,peit,fname_output,fname_initialcond,pall,pavg):
	cdef int nvars=2
	cdef int npars=3
	cdef double *z
	cdef double *zout
	cdef double *dz
	cdef double *p
	cdef int *a
	cdef int it;
	cdef double t
	cdef int i
	cdef int j

	cdef double C=<double>pC
	cdef double tequ=<double>ptequ
	cdef double tmax=<double>ptmax
	cdef double dt=<double>pdt
	cdef int eit=<int>peit

	cdef double sumrkx,sumrky,sumr2,sumr,r,r2,r_k

	# hacemos espacio en la memoria...
	z=<double *>malloc(sizeof(double)*nvars*N)
	zout=<double *>malloc(sizeof(double)*nvars*N)
	dz=<double *>malloc(sizeof(double)*nvars*N)
	p=<double *>malloc(sizeof(double)*npars*N)

	a=<int *>malloc(sizeof(int)*N*N)
	# guardamos en z, p, etc... los valores que ya fueron inicializados y estan guardados en o[i].z, o[i].p, etc...
	for i in xrange(N):
		z[nvars*i]=<double>o[i].x
		z[nvars*i+1]=<double>o[i].y
		p[npars*i]=<double>o[i].omega
		p[npars*i+1]=<double>o[i].a2
		p[npars*i+2]=<double>o[i].gamma

	# guardamos la lista de vecinos en forma de matriz de conectividad
	for i in xrange(N):
		for j in xrange(N):
			if(j in lnghbr[i]):
				a[i*N+j]=1
			else:
				a[i*N+j]=0

	# vamos por las condiciones iniciales
	# si ya estan ahi, las cargamos (y lo de la equilibracion se olvida, incluso si tequ>0)...
	# si no estan, las guardamos (full precision)
	if exists(fname_initialcond):
		# leer
		finitc=open(fname_initialcond,"r")
		line=finitc.readline()
		sline=line.split(' ')
		for i in xrange(N):
			z[2*i+0]=float(sline[i])
			z[2*i+1]=float(sline[i+N])
		finitc.close()
	else:
		# empezamos...! (equilibracion)
		t=0
		for it in xrange(int(tequ/dt)):
			dzdt(t,N,C,p,a,z,dz)
			rk4(z,dz,N,N*nvars,C,t,dt,p,a,zout)
			z=zout

		finitc=open(fname_initialcond,"w")
		for i in xrange(N):
			finitc.write("%.64e " % z[2*i+0])
		for i in xrange(N):
			finitc.write("%.64e " % z[2*i+1])
		finitc.close()

	f=open(fname_output,"w")
	t=0.
	it=0
	while (t<=tmax):
		if(it%eit==0):
			avgx=sum([z[2*i+0] for i in xrange(N)])/float(N)
			avgy=sum([z[2*i+1] for i in xrange(N)])/float(N)

			f.write(str(t)+" ")
			f.write(str(sqrt(avgx**2+avgy**2)))

			# aca es donde agregamos lo nuevo! (que imprima r_k (r_kuramoto) y r_ravg) (y por ahora tambien r_r2avg)
			# calculo los radios, que voy a usar
			sumrkx=0.
			sumrky=0.
			sumr2=0.
			sumr=0.
			for i in xrange(N):
				r2=z[2*i+0]**2+z[2*i+1]**2
				r=sqrt(r2)
				sumrkx+=z[2*i+0]/r
				sumrky+=z[2*i+1]/r
				sumr+=r
				sumr2+=r2

			#r2=[z[2*i+0]**2+z[2*i+1]**2 for i in xrange(N)]
			#r =[sqrt(r2[i]) for i in xrange(N)] 
			#r_ravg=sum(r)/float(N)
			#r_r2avg=sum(r2)/float(N)
			#sumrkx=sum([z[2*i+0]/r[i] for i in xrange(N)])
			#sumrky=sum([z[2*i+1]/r[i] for i in xrange(N)])
			r_k=sqrt(sumrkx**2+sumrky**2)/float(N)

			f.write(" "+str(r_k)+" "+str(sumr/float(N))+" "+str(sumr2/float(N)))

			if(pavg):
				f.write(" "+str(avgx))
				f.write(" "+str(avgy))
			if(pall):
				for i in xrange(N):
					f.write(" "+str(z[2*i+0]))
					f.write(" "+str(z[2*i+1]))
			f.write("\n")

		dzdt(t,N,C,p,a,z,dz)
		rk4(z,dz,N,N*nvars,C,t,dt,p,a,zout)
		#actualizamos y adelantamos dt
		z=zout
		t+=dt
		it+=1

	f.close()
	
	'''
	#y antes de irnos tenemos que limpiar la memoria!!!!
	for i in xrange(N):
		free(z[i])
	free(z)
	for i in xrange(N):
		free(zout[i])
	free(zout)
	for i in xrange(N):
		free(dz[i])
	free(dz)
	for i in xrange(N):
		free(p[i])
	free(p)
	'''

'''
#def runfromcheckpoint(N,o,lnghbr,pC,ptequ,ptmax,pdt,peit,fname_output,fname_initialcond,pall,pavg):
def runfromcheckpoint(N,o,lnghbr,pC,ptequ,ptmax,pdt,peit,fname_output,pall,pavg):
	cdef int nvars=2
	cdef int npars=3
	cdef double *z
	cdef double *zout
	cdef double *dz
	cdef double *p
	cdef int *a
	cdef int it;
	cdef double t
	cdef int i
	cdef int j

	cdef double C=<double>pC
	cdef double tequ=<double>ptequ
	cdef double tmax=<double>ptmax
	cdef double dt=<double>pdt
	cdef int eit=<int>peit

	# hacemos espacio en la memoria...
	z=<double *>malloc(sizeof(double)*nvars*N)
	zout=<double *>malloc(sizeof(double)*nvars*N)
	dz=<double *>malloc(sizeof(double)*nvars*N)
	p=<double *>malloc(sizeof(double)*npars*N)

	a=<int *>malloc(sizeof(int)*N*N)
	
	# guardamos en z, p, etc... los valores que ya fueron inicializados y estan guardados en o[i].z, o[i].p, etc...
	for i in xrange(N):
		z[nvars*i]=<double>o[i].x
		z[nvars*i+1]=<double>o[i].y
		p[npars*i]=<double>o[i].omega
		p[npars*i+1]=<double>o[i].a2
		p[npars*i+2]=<double>o[i].gamma

	# guardamos la lista de vecinos en forma de matriz de conectividad
	for i in xrange(N):
		for j in xrange(N):
			if(j in lnghbr[i]):
				a[i*N+j]=1
			else:
				a[i*N+j]=0

	f=open(fname_output,"w")
	t=0.
	it=0
	while (t<=tmax):
		if(it%eit==0):
			avgx=sum([z[2*i+0] for i in xrange(N)])/float(N)
			avgy=sum([z[2*i+1] for i in xrange(N)])/float(N)

			f.write(str(t)+" ")
			f.write(str(sqrt(avgx**2+avgy**2)))

			if(pavg):
				f.write(" "+str(avgx))
				f.write(" "+str(avgy))
			if(pall):
				for i in xrange(N):
					f.write(" "+str(z[2*i+0]))
					f.write(" "+str(z[2*i+1]))
			f.write("\n")

		dzdt(t,N,C,p,a,z,dz)
		rk4(z,dz,N,N*nvars,C,t,dt,p,a,zout)
		#actualizamos y adelantamos dt
		z=zout
		t+=dt
		eit+=1

	f.close()
'''
