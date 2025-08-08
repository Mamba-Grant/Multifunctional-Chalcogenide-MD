#import mocules
import matplotlib.pyplot as plt
import json
import glob

def plot_band_nosoc(jfile):
    #load data from json file
    with open(jfile, 'r') as file:
        data = json.load(file)

    #get name of structure
    name = jfile.split('/')[-1].split('.')[0]

    #get x and y values
    bands = data['bands'] # num of kpoints x num of bands x 50
    distances = data['band distances'] # num of kpoints x 50 
    ticks = data['KPoints']

    #reformat distances 
    distance = []
    i=0
    while i<len(distances):
        for d in distances[i]:
            distance.append(d)
        i+=1
    #print(len(distance))

    #reformat bands and plot each
    j=0
    while j<len(bands[0]):
        band = []
        i=0
        while i<len(bands):
            for b in bands[i][j]:
                band.append(b)
            
            i+=1
        plt.plot(distance,band)#, color='k')
        j+=1

    #format of plot
    plt.axhline(y=0, ls='--', color='gray')
    plt.xticks(ticks['distance'],ticks['label'])
    plt.grid(axis='x')
    plt.ylim(-4,4)
    
    plt.title(name + ' Band Structure without SOC')
    plt.xlabel('KPOINTS')
    plt.ylabel('ENERGY (eV)')

    #show or save plot
    plt.show()
    #plt.savefig('results/bandPlots/monoMP/'+name+'.png')
    #plt.close()

def plot_band_soc(jfile):
    #load data from json file
    with open(jfile, 'r') as file:
        data = json.load(file)

    #get name of structure
    name = jfile.split('/')[-1].split('.')[0]

    #get x and y values
    bands = data['bands soc'] # num of kpoints x num of bands x 50
    distances = data['band distances soc'] # num of kpoints x 50 
    ticks = data['KPoints']

    #reformat distances 
    distance = []
    i=0
    while i<len(distances):
        for d in distances[i]:
            distance.append(d)
        i+=1
    #print(len(distance))

    #reformat bands and plot each
    j=0
    while j<len(bands[0]):
        band = []
        i=0
        while i<len(bands):
            for b in bands[i][j]:
                band.append(b)
            
            i+=1
        plt.plot(distance,band)#, color='k')
        j+=1

    #format of plot
    plt.axhline(y=0, ls='--', color='gray')
    plt.xticks(ticks['distance'],ticks['label'])
    plt.grid(axis='x')
    plt.ylim(-4,4)
    
    plt.title(name + ' Band Structure with SOC')
    plt.xlabel('KPOINTS')
    plt.ylabel('ENERGY (eV)')

    #show or save plot
    plt.show()
    #plt.savefig('results/bandPlots/monoMP/'+name+'.png')
    #plt.close()
    
def plot_dos(jfile):
    #load data from json file
    with open(jfile, 'r') as file:
        data = json.load(file)

    #get name of structure
    name = jfile.split('/')[-1].split('.')[0]

    #get x and y values
    energy = data['density of states energies']
    tdos = data['total density of states']
    pdos = data['projected density of states']
    const ticks = data['KPoints']

    #plot total density of states
    plt.plot(energy,tdos, label='total')

    #plot each projected dos
    for d in pdos:
        plt.plot(energy,d[1], label=d[0])

    #format plot
    plt.legend()
    plt.axvline(x=0, ls='--', color='gray')
    plt.grid()
    #plt.xlim(-10,10)
    #plt.ylim(0,50)
    
    plt.title(name + ' Density of States')
    plt.xlabel('ENERGY - EFermi (eV)')
    plt.ylabel('Density of States (states/eV)')

    #show or save plot
    plt.show()
    #plt.savefig('results/dosPlots/monoMP/'+name+'.png')
    #plt.close()

#read json file - CHANGE FORMAT
jfile = glob.glob('results/jsons/mono/As2GeTe4-P_3m1.json')




