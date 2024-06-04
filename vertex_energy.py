import os
import matplotlib.pyplot as plt
import ROOT
ROOT.gSystem.Load("libAra.so")
ROOT.gSystem.Load("libSim.so")

import numpy as np


def get_xyz_displacement(origin, position, icemodel):
    """
    Estimates the South Pole as flat earth and returns the x, y, z 
        distance of position to origin
    Not perfect, x and y distances are a bit off

    Parameters
    ----------
    origin : AraSim ROOT.Position()
        Origin of the displacement vector, usually the simulated ARA station.
    position : AraSim ROOT.Position()
        End point of the displacement vector, usually the location of a 
          simulated neutrino interaction. 
    icemodel : AraSim ROOT.IceModel()
        The icemodel used by your AraSim simulation.

    Returns
    -------
    [dX, dY, dZ] : list of floats
        Distance (in meters and cartesian coordinates) of the position with
          respect to the origin.
    """
    # Convert origin coordinates
    r_from_pole_origin = np.sqrt(origin.GetX()**2 + origin.GetY()**2)
    lon_origin = np.radians(origin.Lon())
    lat_origin = np.radians(origin.Lat())
    x_origin = r_from_pole_origin * np.cos(lon_origin)
    y_origin = r_from_pole_origin * np.sin(lon_origin)
    z_origin = icemodel.Surface(lon_origin, lat_origin) - origin.R()
    # Get coordinates of provided position
    r_from_pole_position = np.sqrt(position.GetX()**2 + position.GetY()**2)
    lon_position = np.radians(position.Lon())
    lat_position = np.radians(position.Lat())
    x_position = r_from_pole_position * np.cos(lon_position)
    y_position = r_from_pole_position * np.sin(lon_position)
    z_position = icemodel.Surface(lon_position, lat_position) - position.R()
    return [x_position-x_origin, y_position-y_origin, z_position-z_origin]


files = sorted(os.listdir("/pnfs/iihe/ara/store/user/mvderven/output_ARA_files"))

X = []
Y = []
Z = []

# we get the vertex positions from each file
for i in files : 
	chaine = str(i)
	if "1e11" in chaine : # We open the files with the configuration that we want (Chiba-default/Chiba-new/KU-default/KU-new) or with the energy wanted
		print(i) # Just for verification 
		file =  ROOT.TFile.Open("/pnfs/iihe/ara/store/user/mvderven/output_ARA_files/"+ i) #open the file

		file.AraTree.GetEntry(0) # We have to get the entry for AraTree
		vertex_pos_x = [get_xyz_displacement(file.AraTree.detector.stations[0], at2.event.Nu_Interaction[0].posnu, file.AraTree.icemodel)[0] for at2 in file.AraTree2 if at2.event.Nu_Interaction[0].weight>0.9]
		vertex_pos_y = [get_xyz_displacement(file.AraTree.detector.stations[0], at2.event.Nu_Interaction[0].posnu, file.AraTree.icemodel)[1] for at2 in file.AraTree2 if at2.event.Nu_Interaction[0].weight>0.9]
		vertex_pos_z = [get_xyz_displacement(file.AraTree.detector.stations[0], at2.event.Nu_Interaction[0].posnu, file.AraTree.icemodel)[2] for at2 in file.AraTree2 if at2.event.Nu_Interaction[0].weight>0.9]
		for i in vertex_pos_x:
			X.append(i)
		for j in vertex_pos_y:
			Y.append(j)
		for k in vertex_pos_z:
			Z.append(k)


# save the positions with numpy
np.save("/user/mvderven/pos_X_1e11_trig", X)
np.save("/user/mvderven/pos_Y_1e11_trig", Y)
np.save("/user/mvderven/pos_Z_1e11_trig", Z)
