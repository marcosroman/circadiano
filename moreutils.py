def period(t,f):
	N=len(f)

	uf=[]
	for i in range(N):
		uf.append(np.unwrap(f[i]))

	from scipy.stats import linregress
	pers=[]
	for i in range(N):
		pers.append(2*np.pi/linregress(t,uf[i])[0])

	return pers
