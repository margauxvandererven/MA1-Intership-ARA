import os
import numpy as np
import ROOT
ROOT.gSystem.Load("libAra.so")
ROOT.gSystem.Load("libSim.so")


# ROOT files
files = sorted(os.listdir("/pnfs/iihe/ara/store/user/mvderven/output_ARA_files"))

N_tot = [] # total number of simulated neutrinos
N_trig = [] # total number of triggered neutrinos
N_weight = [] # total weight
V_geo = [] # geometric volume
Energy = [] # energy

for i in files : 
	chaine = str(i)
	if "Chiba-default" in chaine : # We open the files with the configuration that we want (Chiba-default/Chiba-new/KU-default/KU-new)
		print(i) # Just for verification 
		file =  ROOT.TFile.Open("/pnfs/iihe/ara/store/user/mvderven/output_ARA_files/"+ i) #open the file

		file.AraTree.GetEntry(0) # We have to get the entry for AraTree
		NNu = file.AraTree.settings.NNU # Number of neutrinos simulated (triggered and not triggered) = 50 000
		N_tot.append(NNu)	

		N_trig.append(file.AraTree2.GetEntries()) # Number of triggered neutrinos	
		weight = [at2.event.Nu_Interaction[0].weight for at2 in file.AraTree2] # Weight of the neutrino interaction
		k = sum(weight)
		N_weight.append(k) 

		depht = file.AraTree.settings.MAX_POSNU_DEPTH # Depth (in meters) of the simulation volume
		radius = file.AraTree.settings.POSNU_RADIUS # Radius (in meters) of the simulation volume
		exponent = file.AraTree.settings.EXPONENT # Energy 10^x eV, x = (EXPONENT − 400)/10

		energy = 10**((exponent-400)/10)
		Energy.append(energy)

		Vgeo = np.pi*radius**2*depht # Volume of a cylinder 
		V_geo.append(Vgeo)


# We have 5 runs for each configuration, we have to "merge" these. I attribute to each energy
# the sum of weights, total number of events, geometric volumes and triggered events. 

n = len(Energy)

M = Energy+ N_weight
O = Energy+ N_tot
P = Energy + V_geo
Q = Energy + N_trig

W = {} # {energy : sum of weights for the 5 runs}
N = {} # {energy : sum of total for the 5 runs}
V = {} # {energy : sum of geometric volume for the 5 runs}
Nt = {} # {energy : sum of triggered events for the 5 runs}

for i, value in enumerate(M[n:]): 
	if M[i] in W.keys():
		W[M[i]] += value
	else:
		W[M[i]] = value

for i, value in enumerate(O[n:]):
	if O[i] in N.keys():
		N[O[i]] += value
	else:
		N[O[i]] = value

for i, value in enumerate(P[n:]):
        if P[i] in V.keys():
                V[P[i]] += value
        else:
             	V[P[i]] = value

for i, value in enumerate(Q[n:]):
        if Q[i] in Nt.keys():
                Nt[Q[i]] += value
        else:
             	Nt[Q[i]] = value


V_eff = []
# effective volume for each energy
for i in W:
	k = W[i] * V[i]/5 /N[i]*10**(-9) *4*np.pi # Sum of weights * mean geometric volume / Sum of the total events * 10-9 (for km) * solid angle
	V_eff.append(k)

print("Veff",V_eff)
print("Energy", list(dict.fromkeys(W)))


error = []
# error on the effective volume
for i in W:
	e = np.sqrt(Nt[i])* V[i]/5 /N[i]*10**(-9) *4*np.pi
	error.append(e)

print("errors", error)

file.Close()
