
#1. can we make stellar_nu 1D?
#2. check SEDs for bulge_fnu and disk_fnu
#3. add the spherical sources that correspond to the disk and bulge stars and run

#Code:  pd_front_end.py

#=========================================================
#IMPORT STATEMENTS
#=========================================================

import numpy as np
from hyperion.model import Model
import matplotlib as mpl
import matplotlib.pyplot as plt
from hyperion.model import ModelOutput
import h5py

import constants as const
import parameters as par
import sys
import random

from astropy.table import Table
from astropy.io import ascii



import pfh_readsnap
from grid_construction import *
from SED_gen import *


import os.path
#=========================================================
#GRIDDING
#=========================================================

if par.SKIP_GRID_READIN == False:

    if os.path.isfile(par.Auto_TF_file) == False:
        #only create the grid if the grid T/F file doesn't exist already
        
        if par.Manual_TF == True: 
            print 'Grid is coming from a Manually Set T/F Octree'
            refined = np.genfromtxt(par.Manual_TF_file,dtype = 'str')
            dustdens = np.loadtxt(par.Manual_density_file,dtype='float')
            
            #change refined T's to Trues and F's to Falses
            
            refined2 = []
        
            for i in range(len(refined)):
                if refined[i] == 'T':refined2.append(True)
                if refined[i] == 'F':refined2.append(False)
                
                refined = refined2

                print 'Manual grid finished reading in '


        elif par.GADGET_octree_gen == True:
            print 'Octree grid is being generated from the Gadget Snapshot'
            
            refined = gadget_logical_generate(par.Gadget_dir,par.Gadget_snap_num)
        
        elif par.YT_octree_gen == True:
                
            print 'Octree grid is being generated by YT'
                
     
            refined = yt_octree_generate(par.Gadget_snap_name,par.Gadget_dir,par.Gadget_snap_num)
        


    else:
        print 'Grid already exists - no need to recreate it: '+ str(par.Auto_TF_file)
        print 'Instead - reading in the grid.'
                
        #read in the grid if the grid already exists.
        #reading in the refined:
        refined = np.genfromtxt(par.Auto_TF_file,dtype = 'str',skiprows=1)
        pos_data = np.loadtxt(par.Auto_positions_file,skiprows=1)
        xmin = pos_data[:,0]*const.pc*1.e3
        xmax = pos_data[:,1]*const.pc*1.e3
        ymin = pos_data[:,2]*const.pc*1.e3
        ymax = pos_data[:,3]*const.pc*1.e3
        zmin = pos_data[:,4]*const.pc*1.e3
        zmax = pos_data[:,5]*const.pc*1.e3
            
        xcent = np.mean([min(xmin),max(xmax)])
        ycent = np.mean([min(ymin),max(ymax)])
        zcent = np.mean([min(zmin),max(zmax)])
            
        #dx,dy,dz are the edges of the parent grid
        dx = (max(xmax)-min(xmin))/2.
        dy = (max(ymax)-min(ymin))/2.
        dz = (max(zmax)-min(zmin))/2.
        


            
        dustdens_data = np.loadtxt(par.Auto_dustdens_file,skiprows=1)
        dustdens = dustdens_data[:]
            
        #change refined T's to Trues and F's to Falses
        refined2 = []
        
        for i in range(len(refined)):
            if refined[i] == 'True':refined2.append(True)
            if refined[i] == 'False':refined2.append(False)
        refined = refined2
            

            #end gridding
                


#generate the SEDs 

#stellar_nu,fnu are of shape (nstars,nlambda);
#stellar_mass is the mass of the star particles, and therefore
#(nstars) big.
#stellar_pos is (nstars,3) big



#generate teh stellar masses, positions and spectra
stellar_pos,disk_positions,bulge_positions,stellar_masses,stellar_nu,stellar_fnu,disk_fnu,bulge_fnu= new_sed_gen(par.Gadget_dir,par.Gadget_snap_num)
pdb.set_trace()

nstars = stellar_fnu.shape[0]

#potentially write the stellar SEDs to a npz file
if par.STELLAR_SED_WRITE == True:
    np.savez('stellar_seds.npz',stellar_nu,stellar_fnu,disk_fnu,bulge_fnu)


#debugging parameter
if par.SOURCES_IN_CENTER == True:
    for i in range(nstars):
        stellar_pos[:,0] = 0
        stellar_pos[:,1] = 0
        stellar_pos[:,2] = 0



pdb.set_trace()

#========================================================================
#Initialize Hyperion Model
#========================================================================
if par.SUPER_SIMPLE_SED == False:
    m = Model()
    if par.Grid_Type == 'Octree':
        m.set_octree_grid(xcent,ycent,zcent,
                          dx,dy,dz,refined)


        m.add_density_grid(dustdens,par.dustfile)
else:

    m = Model()
    

    #set up the coordinates of the octree
 

    x=0
    y=0
    z=0
    dx = const.pc*100
    dy = const.pc*100
    dz = const.pc*100
    #dx = 7.e23
    #dy = 7.e23
    #dz = 7.e23


    refined = [True,False,False,False,False,False,False,False,False]

    #define the grid
    m.set_octree_grid(x,y,z,dx,dy,dz,refined)
    m.add_density_grid(np.ones(m.grid.shape)*4.e-20,par.dustfile)
    
    



  


#generate dust model. This needs to preceed the generation of sources
#for hyperion since the wavelengths of the SEDs need to fit in the dust opacities.

df = h5py.File(par.dustfile,'r')
o = df['optical_properties']
df_nu = o['nu']
df_chi = o['chi']

df.close()




#add sources to hyperion

for i in range(nstars):
    nu = stellar_nu[:]
    fnu = stellar_fnu[i,:]


    nu_inrange = np.logical_and(nu >= min(df_nu),nu <= max(df_nu))
    nu_inrange = np.where(nu_inrange == True)[0]
    nu = nu[nu_inrange]

    #reverse the arrays for hyperion
    nu = nu[::-1]
    fnu = fnu[::-1]

    fnu = fnu[nu_inrange]

    lum = np.absolute(np.trapz(fnu,x=nu))*stellar_masses[i]/const.msun #since stellar masses are in cgs, and we need them to be in msun



    if par.SUPER_SIMPLE_SED == False:
        m.add_spherical_source(luminosity = lum,
                               spectrum = (nu,fnu),
                               position = (stellar_pos[i,0],stellar_pos[i,1],stellar_pos[i,2]),
                               radius = par.stellar_softening_length*const.pc*1.e3)
    else:

       
      
        posx = ((-1.)**i)*random.random()*dx
        posy = ((-1.)**(i+1))*random.random()*dy
        posz = ((-1.)**i)*random.random()*dz
            
            
        
        m.add_spherical_source(luminosity = 1.e3*const.lsun,spectrum = (nu,fnu), radius = 10.*const.rsun,position=(posx,posy,posz))
       



print 'Done adding Sources'

print 'Setting up Model'
#set up the SEDs and images
m.set_raytracing(True)
m.set_n_photons(initial=1.e6,imaging=1.e6,
                raytracing_sources=1.e6,raytracing_dust=1.e6)
#m.set_n_initial_iterations(7)
m.set_convergence(True,percentile=80.,absolute=5,relative=1.05)


image = m.add_peeled_images(sed = True,image=False)
image.set_wavelength_range(250,0.01,5000.)
image.set_viewing_angles(np.linspace(0,90,par.NTHETA),np.repeat(20,par.NTHETA))
image.set_track_origin('basic')

print 'Beginning RT Stage'
#Run the Model
m.write('example.rtin')
m.run('example.rtout',mpi=True,n_processes=3)














