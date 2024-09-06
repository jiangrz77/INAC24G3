# -*- coding: utf-8 -*-
"""
Created on Wed 4th.Sep 2024

@author: Bingyang Tan
"""

import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import scipy as sp
import matplotlib.ticker as ticker
import re


def round_to_N(n, direction='nearest', N=50):
    if direction == 'up':
        return ((n + 49) // 50) * 50
    elif direction == 'down':
        return (n // 50) * 50
    else:
        return round(n / 50) * 50

def deduplicate_var_names(var_names):
    seen = {}
    new_var_names = []
    for name in var_names:
        if name in seen:
            seen[name] += 1
            new_name = f"{name}_{seen[name]}"
        else:
            seen[name] = 0
            new_name = name
        new_var_names.append(new_name)
    return new_var_names
    
class FranecData():
    path = None
    def __init__(self, path: str):
        """
        Initialize the Franec object.

        Args:
            path (str): Directory of the data file.
        """
        self.path = path
        return None
    
class mod_chi(FranecData):
    index = None
    mass = None
    var_names = None
    look_back_time = None
    
    def data(self, var_name: str, dtype = float) -> np.ndarray:
        df = pd.read_csv(
            self.path+f'/mods/%07d.chi'%self.index, 
            sep='\s+', 
            skiprows=1, 
            names=self.var_names, 
            usecols=[var_name], 
            engine='python',
            skipinitialspace=True,
            dtype=dtype
            )
        return df[var_name].values
    
    def __init__(self, path:str, index:int):
        FranecData.__init__(self, path=path)
        self.index = index
        with open(self.path+f'/mods/%07d.chi'%self.index, 'r') as file:
            self.var_names = re.split(r'\s{2,}', file.readline().strip())
        self.mass = self.data("M")
        return None  

    def co_core(
        self, crit_he=1e-2, crit_o=0.3, 
        crit_c=5e-2, crit_nuc='o')-> tuple:
        """
        find where
            he4 mass fraction > crit_he, and
            
            o16 mass fraction > crit_o, or
            c12 mass fraction > crit_c
        
        return index of mod_chi.data() and CO core mass.
        """
        he_mf = self.data('He4')
        match crit_nuc:
            case 'o' :
                o_mf = self.data('O16')
                for i in range(0, len(self.mass)):
                    if he_mf[i]>crit_he and o_mf[i]>crit_o:
                        return i, self.mass[i]
            case 'c' :
                c_mf = self.data("c12")
                for i in range(0, len(self.mass)):
                    if he_mf[i]>crit_he and c_mf[i]>crit_c:
                        return i, self.mass[i]
            case _ :
                print("CO core not found")
                return None
    
    def draw_mf(
        self,
        nucs=[],
        title=None,
        ylim=[1e-8, 1.5],
        xlim=None,
        yscale='log',
        legend=True,
        legend_loc='center right',
        legend_frameon=False,
        show=False
        ) -> None:
        if xlim is None:
            xlim=[0, self.mass[-1]]
        for nuc in nucs:
            plt.plot(self.mass, self.data(nuc), label=nuc)
        plt.ylim(ylim[0], ylim[1])
        plt.xlim(xlim[0], xlim[1])
        plt.yscale(yscale)
        if legend:
            plt.legend(loc=legend_loc, frameon=legend_frameon)
        plt.xlabel('enclosed mass (solar mass)')
        plt.ylabel('mass fraction')
        if not title is None:
            #plt.title(r'$\log(\tau_{-1}-\tau)+0.5$%.2f'%)
            plt.title(title)
        if show:
            plt.show()
    
class mod_f01(FranecData):
    index = None
    mass = None
    var_names = None
    
    def data(self, var_name: str, dtype = float) -> np.ndarray:
        df = pd.read_csv(
            self.path+f'/mods/%07d.f01'%self.index, 
            sep='\s+', 
            skiprows=1, 
            names=self.var_names, 
            usecols=[var_name], 
            engine='python',
            skipinitialspace=True,
            dtype=dtype
            )
        return df[var_name].values
    
    def __init__(self, path:str, index:int):
        FranecData.__init__(self, path=path)
        self.index = index
        with open(self.path+f'/mods/%07d.f01'%self.index, 'r') as file:
            var_names = re.split(r'\s{2,}', file.readline().strip())
        self.var_names = deduplicate_var_names(var_names) + ['xxx']
        self.mass = self.data("M/MTOT")
        return None  
            
class gra_fisica(FranecData):
    model = None
    var_names = None
    mods_index = None
    
    def data(self, var_name: str, dtype = float) -> np.ndarray:
        df = pd.read_csv(
            self.path+'/grafica/gra_fisica', 
            sep='\s+', 
            skiprows=1, 
            names=self.var_names, 
            usecols=[var_name], 
            engine='python',
            skipinitialspace=True,
            dtype=dtype
            )
        return df[var_name].values
    
    def __init__(self, path:str):
        FranecData.__init__(self, path=path)
        # 读取文件的前几行来获取列名
        with open(self.path+'/grafica/gra_fisica', 'r') as file:
            self.var_names = re.split(r'\s{2,}', file.readline().strip())
        self.var_names = deduplicate_var_names(self.var_names)
        self.model = self.data("nmod", dtype=int)
        self.mods_index = list(range(
            round_to_N(self.model[0], 'up'),
            round_to_N(self.model[-1], 'down') + 50,
            50))
        
        return None
              
class bigtab(FranecData):
    model = None
    var_names = None
    mods_index = None
    c12_cen = None
    
    def data(self, var_name: str, dtype = float) -> np.ndarray:
        df = pd.read_csv(
            self.path+'/out/bigtab.txt', 
            sep='\s+', 
            skiprows=1, 
            names=self.var_names, 
            usecols=[var_name], 
            engine='python',
            skipinitialspace=True,
            dtype=dtype
            )
        return df[var_name].values
    
    def __init__(self, path:str):
        FranecData.__init__(self, path=path)
        # 读取文件的前几行来获取列名
        with open(self.path+'/out/bigtab.txt', 'r') as file:
            self.var_names = re.split(r'\s{2,}', file.readline().strip())
        self.model = self.data("Model", dtype=int)
        self.mods_index = list(range(
            round_to_N(self.model[0], 'up'),
            round_to_N(self.model[-1], 'down') + 50,
            50))
        
        self.c12_cen = []
        for index in  self.mods_index:
            prof = mod_chi(self.path, index)
            self.c12_cen.append(prof.data("C12")[0])
        self.c12_cen = np.array(self.c12_cen)
        
        return None
    
    
    def look_back_time(self) -> np.ndarray:
        """
        Get look back time defined as log10(t_final - t).

        Returns:
            np.ndarray: The look back time data corresponding to every model.
        """
        age = self.data('Age(yr)')
        xx = age[-1]
        age = xx-age
        #Avoid boundary zeros
        age[-1] = age[-1] / 2.0
        age[0] = age[1] / 2.0
        age = np.log10(age)
        return age
    
    def when_he_depl(self, crit=1e-5) -> int:
        for i, item in enumerate(self.data('He-cen')):
            if item < crit:
                break
        return round_to_N(self.model[i], 'up')
    
    def when_c_ign(self, crit=3e-2) -> int:
        start = self.mods_index.index(self.when_he_depl())
        c_mf_ini = self.c12_cen[start]
        for i in range(start, len(self.mods_index)):
            if c_mf_ini - self.c12_cen[i] > c_mf_ini * crit:
                break
        return round_to_N(self.mods_index[i])
    
    def draw_Tc_Rho(
        self, 
        xlim=[0, 10],
        ylim=[6.5, 10],
        label='', 
        legend=False,
        show=False
        ):
        plt.plot(self.data("Log Rhoc"), self.data("log Tc"), label=label)
        plt.xlim(xlim[0], xlim[1])       
        plt.ylim(ylim[0], ylim[1])
        if legend:
            plt.legend(loc='center right', frameon=False)
        if show:
            plt.show()     
        
def draw_mf_and_eps(
    path, 
    model_number, 
    nucs=["H", "He4", "C12", "Ne20", "O16"]):
    chi = mod_chi(path=path, index=model_number)
    f01 = mod_f01(path=path, index=model_number)
    xx = f01.mass
    yy = np.log10(f01.data("E-NUC"))
    
    fig, ax1 = plt.subplots()
    for nuc in nucs:
        ax1.plot(xx, chi.data(nuc)[:-1], label=nuc)
    ax1.set_yscale('log')
    ax1.set_ylim(1e-8, 1.5)
    ax1.set_xlabel("enclosed mass (solar mass)")
    ax1.set_ylabel("mass fraction")
    ax1.legend(loc='lower left', frameon=False)
    
    ax2 = ax1.twinx()
    ax2.plot(xx, yy, label='log(E_NUC)', color='k', linestyle='--')
    ax2.set_ylabel("log(E-NUC)")
    
    return None
    