"""
Plots gridded 3D source products produced by LMA_flash_sort_and_grid.py
USAGE:
python LMA_source_plot_cartopy.py {network} {year} {month} {day}
"""

import os
import sys
import subprocess
import glob

import numpy as np
from datetime import datetime, timedelta
from netCDF4 import Dataset

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.axes import Axes
from matplotlib import gridspec, colors
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader
from cartopy.mpl.geoaxes import GeoAxes

from LMA_info import info
from LMA_util import get_lma_data_dir, get_lma_out_dir

GeoAxes._pcolormesh_patched = Axes.pcolormesh

def draw_map(ax, network='DCLMA',
             lat_0=38.8894, lon_0=-77.03517,
             plotrgba=[.94,.96,.98,1],
             continentrgba=[.95,.93,.91,1],
             countiesrgba=[.9,.9,.9,1],
             statesrgba=[.7,.8,1,1],
             coastrgba=[.2,.2,.2,1],
             stationrgba = [0,.8,0,1],
             **kwargs):

    print('\tGenerate Map...')
    projection = ccrs.PlateCarree()

    states_provinces = cfeature.NaturalEarthFeature(
        category='cultural',
        name='admin_1_states_provinces_lines',
        scale='50m',
        facecolor='none')

    #--add features, such as lakes, river, borders, coastlines, etc.
    reader = shpreader.Reader('countyl010g.shp')
    print("\tCreated Reader...")

    counties = list(reader.geometries())
    COUNTIES = cfeature.ShapelyFeature(counties, projection)


    ax.add_feature(cfeature.LAND, color=continentrgba)
    ax.add_feature(COUNTIES, facecolor='none', edgecolor=countiesrgba)
    ax.add_feature(states_provinces, edgecolor=statesrgba)
    ax.add_feature(cfeature.LAKES, color=plotrgba)
    ax.add_feature(cfeature.OCEAN, color=plotrgba)
    ax.coastlines(resolution='10m', color=coastrgba)

    print("\tAdded Features...")

    # offset=3.8
    # extent=[lon_0-offset,lon_0+offset,lat_0-offset, lat_0+offset]
    extent400km = {
        'DCLMA' : [-81.4902, -72.2216, 35.1883, 42.3689],
        'MALMA' : [-80.6803, -71.4599, 34.8194, 42.0002],
        'WFFLMA' : [-79.9485, -70.7802, 34.4132, 41.5943]
    }
    ax.set_extent(extent400km[network], crs=projection)
    print("\tSet Extent...")
    ax.set_aspect('auto')

    print("\tSet Aspect...")

    # -------------- Gather network specific variables  --------------
    lma_info = info(network)
    station_lats = lma_info[2]
    station_lons = lma_info[3]

    print("\tGot Info...")

    # ------------------- Plot LMA Stations -------------------
    ax.scatter(station_lons, station_lats, s=6, marker='s',
              color=stationrgba, facecolors='none',
              transform=projection, zorder=10)

    print("\tDone Generate Map...")
    
    return ax

def round_time(dt, round_to=60):
   seconds = (dt - dt.min).seconds
   rounding = (seconds+round_to/2) // round_to * round_to
   return dt + timedelta(0,rounding-seconds,-dt.microsecond)

def get_data(file, lon_index=(0, 800), lat_index=(0,800), alt_index=(0,20)):

    print('\tGet data from 3d.nc file...')
    # -------- Import Variables from Gridded NetCDF file ------------
    data = Dataset(file).variables
    lons = data['longitude'][:]
    lats = data['latitude'][:]
    grid_type = data['lma_source'][0,:,:,:]
    grid_units = data['lma_source'].units
    time = data['time'][:]
    time_units = data['time'].units
    alts = data['altitude'][:]

    # ------------ Index Data in Region of Interest ------------
    if len(alt_index) > 0:
        lons = data['longitude'][lon_index[0] : lon_index[1]]
        lats = data['latitude'][lat_index[0] : lat_index[1]]
        alts = data['altitude'][alt_index[0] : alt_index[1]]
        grid_type = data['lma_source'][0, lon_index[0] : lon_index[1],
                    lat_index[0] : lat_index[1], alt_index[0] : alt_index[1]]

    # ------------- Extract date from Gridded NetCDF file -------------
    base_date = datetime.strptime(time_units, "seconds since %Y-%m-%d %H:%M:%S")
    time_delta = timedelta(0,float(time[0]),0)
    start_time = base_date + time_delta

    fname = os.path.basename(file)
    frame_interval = int(fname.split('_')[3]) # split filename to get frame interval

    # start_time = round_time(start_time, round_to=frame_interval)
    start_time = round_time(start_time, round_to=60*10)

    print('\t\tCalculate summations...')
    # ------------------- Sum TOTAL Source Count -------------------
    total = np.sum(grid_type)

    # ---------- Create lat/lon mesh -------------
    mesh_lon, mesh_lat = np.meshgrid(lons, lats)

    # ------------------ Initiate Summation Arrays ------------------
    lmalon = np.zeros((grid_type.shape[0],grid_type.shape[2]))
    lmalat = np.zeros((grid_type.shape[1],grid_type.shape[2]))
    lmalonlat = np.zeros((grid_type.shape[0],grid_type.shape[1]))

    # --------------- Sum Horizontal Source Counts ------------------
    lmalon = np.sum(grid_type,axis=1)
    lmalat = np.sum(grid_type,axis=0)
    lmaalt = np.sum(grid_type,axis=(0,1))

    # ---------------- Sum Vertical Source Counts -------------------
    lmalonlat = np.sum(grid_type,axis=2)

    # ------------------ Mask source values <= 0 --------------------
    lmalon = np.ma.masked_where(lmalon <= 0, lmalon)
    lmalat = np.ma.masked_where(lmalat <= 0, lmalat)
    lmalonlat = np.ma.masked_where(lmalonlat <= 0, lmalonlat)

    DATA = dict(mesh_lon=mesh_lon, mesh_lat=mesh_lat,
                alts=alts,
                lmalon=lmalon,lmalat=lmalat,
                lmalonlat=lmalonlat,lmaalt=lmaalt,
                total=total,
                grid_units=grid_units,
                grid_type=grid_type,
                start_time=start_time,
                frame_interval=frame_interval)

    return DATA

def make_plot(data,file,
              grid_name='gridded_product',
              network='DCLMA',
              outpath='./',
              do_save=True,
              theme = 'normal',
              image_type='png',):

    lma_info = info(network)
    lat_0 = lma_info[0]
    lon_0 = lma_info[1]

    # --------------------- Setup ColorMap --------------------------
    vmin = data['grid_type'][:].min()
    vmax = 500 # data['grid_type'].max()
    cmap = colors.ListedColormap(['#7e00ff','#0000ff','#007eff','#00ffff',
                                    '#00ff00','#007e3e','#3e7e7e','#ffff00',
                                    '#ffbe7e','#ff7e00','#ff007e','#ff0000',
                                    '#be0000','#7e0000','#000000','#7e7e7e',
                                    '#bebebe','#ffffff'])
    cticks=[1,2,4,6,9,11,16,22,30,42,59,78,107,145,197,269,367,500]
    cbounds=[1,2,4,6,9,11,16,22,30,42,59,78,107,145,197,269,367,500]
    norm = colors.BoundaryNorm(cbounds, cmap.N)

    # ---------------- Setup Figure Color Theme ---------------------
    if theme == 'diagnostics':
        fbgrgba = [.95,.95,.95,1]
        edgergba = [.5,.5,.5,1]
        meshrgba = [.7,.5,.7,.01]
        borderrgba = edgergba
        plotrgba = [.9,.9,.95,1]
        gridrgba = [1,.4,.8,.5]
        stationrgba = [0,1,0,1]
        textrgba = [0,0,0,1]
        continentrgba=[.95,.95,.95,1]
        countiesrgba=[.9,.9,.9,1]
        statesrgba=[.7,.8,1,1]
        coastrgba=[.2,.2,.2,1]
    elif theme == 'dark':
        fbgrgba = [0,0,0,1]
        edgergba = [.9,.9,.9,1]
        meshrgba = [.7,.5,.7,0]
        borderrgba = edgergba
        plotrgba = [0,0,0,1]
        gridrgba = [1,.4,.8,.2]
        stationrgba = [0,.7,0,1]
        textrgba = [.9,.9,.9,1]
        continentrgba=[.1,.05,.05,1]
        countiesrgba=[.15,.15,.15,1]
        statesrgba=[.4,.5,.7,1]
        coastrgba=[.8,.8,.8,1]
    else:
        fbgrgba = [1,1,1,1]
        edgergba = [0,0,0,1]
        meshrgba = [.7,.5,.7,0]
        borderrgba = edgergba
        plotrgba = [.94,.96,.98,1]
        gridrgba = [1,.4,.8,0.1]
        stationrgba = [0,.8,0,1]
        textrgba = [0,0,0,1]
        continentrgba=[.95,.93,.91,1]
        countiesrgba=[.9,.9,.9,1]
        statesrgba=[.7,.8,1,1]
        coastrgba=[.2,.2,.2,1]

    # ==============================================================
    # ------------- Generate Figure with Subplot Specs -------------
    print('\tCreate Figure...')

    # -------- Calcualte Figure Size from Subplot Aspect Ratios --------
    F0 = 4.5  # main panel is F0 times the size of the cross section panel
    F1 = 0.25 # cbar panel is F1 times the size of the cross section panel
    F2 = 0.6  # Gap above cbar is F2 times the size of the cross section panel

    fwin = 6  # figure width in inches
    dpi = 300

    mpl.pyplot.rc('axes',linewidth=1,edgecolor=edgergba) # assign axes edge colors

    fig = plt.figure(figsize=(fwin,fwin*(1+F0+F2+F1)/(1+F0)),
                     dpi=dpi,
                     facecolor=fbgrgba,
                     edgecolor=borderrgba,linewidth=2,
                     frameon=True,
                     tight_layout=True)

    gs = fig.add_gridspec(4, 2,
                          width_ratios=(F0,1),
                          height_ratios=(1,F0,F2,F1),
                          left=0.1, right=0.9, bottom=0.1, top=0.9,
                          wspace=0, hspace=0)

    # ===============================================================
    # ----------------- Plan View Composite (main) ------------------
    ax0 = fig.add_subplot(gs[1,0],
                          facecolor=plotrgba,
                          frame_on=True,
                          xscale='linear',yscale='linear',
                          projection=ccrs.PlateCarree())

    map = draw_map(ax0, network=network,
                 lat_0=lat_0, lon_0=lon_0,
                 plotrgba=[.94,.96,.98,1],
                 continentrgba=[.95,.93,.91,1],
                 countiesrgba=[.9,.9,.9,1],
                 statesrgba=[.7,.8,1,1],
                 coastrgba=[.2,.2,.2,1],
                 stationrgba = [0,.8,0,1])

    # -------------------- Create x/y mesh -------------------------
    mesh_xyx = np.zeros(data['mesh_lon'].shape)
    mesh_xyy = np.zeros(data['mesh_lat'].shape)
    mesh_xyx, mesh_xyy = data['mesh_lon'], data['mesh_lat']

    map.pcolormesh(data['mesh_lon'], data['mesh_lat'], data['lmalonlat'].T[:-1,:-1],
                  transform=ccrs.PlateCarree(), edgecolor=meshrgba,
                  cmap=cmap, norm=norm,
                  shading='flat', zorder=10)

    # ===============================================================
    # ---------- East-West Composite Cross Section (top) ------------

    # ----------------------- Create x/z mesh -----------------------
    row = np.floor(mesh_xyx.shape[0]/2) # find middle row of mesh_xyx
    row = np.array(row,dtype='int')     # convert row index to integer value
    xvec = mesh_xyx[row,:]              # index the middle row of mesh_xyx

    mesh_xzx,mesh_xzz = np.meshgrid(xvec,data['alts'])

    # ------------------ Add subplot Axis and Plot ------------------
    ax1 = fig.add_subplot(gs[0,0], sharex=ax0,
                          facecolor=plotrgba,
                          frame_on=True,
                          xscale='linear', yscale='linear')
    plot_xz = ax1.pcolormesh(mesh_xzx,mesh_xzz/1e3,data['lmalon'].T[:-1,:-1],
                             edgecolor=meshrgba,
                             cmap=cmap, norm=norm,
                             shading='flat', zorder=10)
    #plot_xz.cmap.set_over('w')

    # ===============================================================
    # --------- North-South Composite Cross Section (right) ---------
    ax2 = fig.add_subplot(gs[1,1:2], sharey=ax0,
                          facecolor=plotrgba,
                          frame_on=True,
                          xmargin=0, ymargin=0,
                          xscale='linear', yscale='linear')

    # -------------------- Create z/y mesh -------------------------
    col = np.floor(mesh_xyy.shape[1]/2) # find middle column of mesh_xyy
    col = np.array(col,dtype='int')     # convert column to integer value
    yvec = mesh_xyy[:,col]              # index the middle row of mesh_xyy

    mesh_zyz,mesh_zyy = np.meshgrid(data['alts'],yvec)

    # --------------- Add subplot Axis and Plot --------------------
    plot_zy = ax2.pcolormesh(mesh_zyz/1e3,mesh_zyy,data['lmalat'][:-1,:-1],
                             edgecolor=meshrgba,
                             cmap=cmap, norm=norm,
                             shading='flat', zorder=10)
    #plot_zy.cmap.set_over('w')

    # ===============================================================
    # -------------- Total Sounce Count (top-right) -----------------
    ax3 = fig.add_subplot(gs[0,1],
                          facecolor=plotrgba,
                          frame_on=True,
                          xmargin=0,ymargin=0,
                          xscale='linear',yscale='linear')

    ax3.plot(data['lmaalt'],data['alts']/1e3,
             linestyle='-',linewidth=1,marker='None',
             color=borderrgba)
    if data['lmaalt'].max()>0:
        ax3.set_xlim([0,1.1*data['lmaalt'].max()])
    else:
        ax3.set_xlim([0,1.1])

    txtx = ax3.get_xlim()
    txty = ax3.get_ylim()
    ax3.text(txtx[1]*0.05, txty[1]*0.95,'N: ' + str(data['total']),
             horizontalalignment='left',
             verticalalignment='top',
             fontdict=dict(family='PT Sans',size=10),
             color=textrgba,alpha=textrgba[3])

    # ===============================================================
    # ------------------- Add/Format Colorbar -----------------------
    ax4 = fig.add_subplot(gs[3,:])
    cbar = fig.colorbar(ax=ax4, cax=ax4, ticks=cticks,
                        orientation='horizontal',
                        mappable=mpl.cm.ScalarMappable(norm=norm, cmap=cmap))
    cbar.set_label(data['grid_units'],
                   fontdict=dict(family='PT Sans',size=12),
                   color=textrgba,alpha=textrgba[3])

    # Plot Title
    fig.suptitle(network+': Source Density\n'+ str(data['start_time']) + ' - ' + str((data['start_time'] + timedelta(seconds=data['frame_interval'])).strftime("%H:%M:%S"))+' UTC',
                 x=0.5,y=0.98,
                 fontdict=dict(family='PT Sans',size=12),
                 color=textrgba,alpha=textrgba[3])

    # ===============================================================
    # ------------- Finish Setting the Layout Parameters ------------
    # ----------------------- x/y tick labels -----------------------
    ax0.tick_params(axis='both',
                    which='both',
                    direction='in',
                    pad=3, labelsize=10,
                    color=edgergba,
                    labelcolor=textrgba,
                    labeltop=False,
                    labelright=False,
                    bottom=True, top=True,
                    left=True, right=True)
    ax1.tick_params(axis='both',
                    which='both',
                    direction='in',
                    pad=3, labelsize=10,
                    color=edgergba,
                    labelcolor=textrgba,
                    labelbottom=False,
                    bottom=True, top=True,
                    left=True, right=True)
    ax2.tick_params(axis='both',
                    which='both',
                    direction='in',
                    pad=3, labelsize=10,
                    color=edgergba,
                    labelcolor=textrgba,
                    labelleft=False,
                    bottom=True, top=True,
                    left=True, right=True)
    ax3.tick_params(axis='y',
                    which='both',
                    direction='in',
                    pad=3, labelsize=10,
                    color=edgergba,
                    labelcolor=textrgba,
                    bottom=False, top=False,
                    left=True, right=True)
    ax4.tick_params(axis='x',
                    which='major',
                    direction='in',
                    pad=3, labelsize=10,
                    color=edgergba,
                    labelcolor=textrgba,
                    bottom=True, top=True,
                    left=False, right=False)

    # Place tick marks every 100 kilometers
    # ticklabels = np.arange(-400,500,100)
    ticklabels = ['', '-300', '-200','-100','0','100','200','300','']
    if network == 'DCLMA':
        ticklocationx = np.linspace(-81.4902, -72.2216, num=9)
        ticklocationy = np.linspace(35.1883, 42.3689, num=9)
    elif network == 'MALMA':
        ticklocationx = np.linspace(-80.6803, -71.4599, num=9)
        ticklocationy = np.linspace(34.8194, 42.0002, num=9)
    elif network == 'WFFLMA':
        ticklocationx = np.linspace(-79.9485, -70.7802, num=9)
        ticklocationy = np.linspace(34.4132, 41.5943, num=9)

    ax0.set_xticks(ticklocationx)
    ax0.set_yticks(ticklocationy)
    ax0.set_xticklabels(ticklabels)
    ax0.set_yticklabels(ticklabels)

    # Remove tick labels from cross section shared axis
    ax3.set_xticks([])
    ax3.set_xticklabels([])
    ax3.set_yticklabels([])

    # Change tick label font
    for tick in ax0.get_xticklabels():
        tick.set_fontname('PT Sans')
    for tick in ax0.get_yticklabels():
        tick.set_fontname('PT Sans')

    for tick in ax1.get_xticklabels():
        tick.set_fontname('PT Sans')
    for tick in ax1.get_yticklabels():
        tick.set_fontname('PT Sans')

    for tick in ax2.get_xticklabels():
        tick.set_fontname('PT Sans')
    for tick in ax2.get_yticklabels():
        tick.set_fontname('PT Sans')

    for tick in ax4.get_xticklabels():
        tick.set_fontname('PT Sans')

    # -------------- Turn plot gridlines on ---------------------
    ax0.grid(visible=True,which='both',axis='both',
            linestyle='-',linewidth=1,color=gridrgba,
            alpha=gridrgba[3])

    ax1.grid(visible=True,which='both',axis='both',
            linestyle='-',linewidth=1,color=gridrgba,
            alpha=gridrgba[3])
    ax2.grid(visible=True,which='both',axis='both',
            linestyle='-',linewidth=1,color=gridrgba,
            alpha=gridrgba[3])
    ax3.grid(visible=True,which='both',axis='y',
            linestyle='-',linewidth=1,color=gridrgba,
            alpha=gridrgba[3])

    # -------------------- axis labels --------------------------
    ax0.set_xlabel('East-West Distance (km)',fontdict=dict(family='PT Sans',size=12),
                   color=textrgba,alpha=textrgba[3])
    ax2.set_xlabel('Alt (km)',fontdict=dict(family='PT Sans',size=12),
                   color=textrgba,alpha=textrgba[3])

    ax0.set_ylabel('North-South Distance (km)',fontdict=dict(family='PT Sans',size=12),
                   color=textrgba,alpha=textrgba[3])
    ax1.set_ylabel('Alt (km)',fontdict=dict(family='PT Sans',size=12),
                   color=textrgba,alpha=textrgba[3])

    # ===============================================================
    # ----------------------- Save file ------------------------------
    print('\tSave Plot')
    filepathway = file.split('/')
    filename = filepathway[-1].split('.')
    filename = "".join(filename[:-1])
    filename = "".join([outpath, filename,'.',image_type])
    if do_save:
        plt.savefig(filename, dpi=dpi,
                    bbox_inches='tight',
                    facecolor = fbgrgba,
                    edgecolor = edgergba,)
    plt.close(fig)

# ===========================================================
# ----------------------- MAIN SCRIPT -----------------------
# ===========================================================

# ---------- Assign Date Variables from User Input ----------
network = sys.argv[1]
year  = sys.argv[2]
month = sys.argv[3]
day   = sys.argv[4]

# --------------- Declair IO Directories --------------------
out_dir = get_lma_out_dir()
grid_dir = f'{out_dir}{network}/grid_files/'
plot_dir = f'{out_dir}{network}/maps/'

# --------------- User input parameters --------------------
params = {'lon_index':(0,800),
          'lat_index':(0,800),
          'alt_index':(0,20)} #km

# ---------- Create Directory for Output Files --------------
date = f'{year}/{month}/{day}/'
outpath = f'{plot_dir}{date}'
if os.path.exists(outpath) == False:
    os.makedirs(outpath)
    subprocess.call(['chmod', 'a+w', outpath, plot_dir + year + '/' +
                    month, plot_dir + year])

# ------------- Get List of 3D Gridded Files ----------------
filepaths = glob.glob(f'{grid_dir}{date}*source_3d.nc')

# -----------------------------------------------------------
# -------------- Generate and Save the Plots ----------------
print(f'grid_dir = {grid_dir}')
print(f'plot_dir = {plot_dir}')
print('Cycle through 3D gridded files.....')

for file in filepaths:
    # ------------ Get Data from Gridded NetCDF Files ------------
    print(file)
    data = get_data(file,
                    lon_index=params['lon_index'],
                    lat_index=params['lat_index'],
                    alt_index=params['alt_index'])
    # --------------------- Generate Figure ---------------------
    make_plot(data,file,
              grid_name='src_density',
              network=network,
              outpath=outpath,
              do_save=True,
              theme='norm',
              image_type='png')

# ===============================================================
