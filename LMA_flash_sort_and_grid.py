#!/usr/bin/env python
"""
Use lmatools to sort LMA ASCII data into flashes
Create gridded imagery from those flashes.
The params dictionary controls the flash sorting parameters.
USAGE:
python LMA_flash_sort_and_grid.py {network} {year} {month} {days}

network: DCLMA, WFFLMA, MALMA
year: 20XX
month: XX
days: XX (multiple days separated by spaces)
"""
import sys, os, glob
from datetime import datetime, timedelta
import subprocess

from lmatools.io.LMA import LMADataset
from lmatools.flashsort.gen_autorun import logger_setup, sort_files
from lmatools.flashsort.gen_sklearn import DBSCANFlashSorter

from lmatools.grid.make_grids import grid_h5flashfiles, dlonlat_at_grid_center, write_cf_netcdf_latlon, write_cf_netcdf_3d_latlon
from six.moves import map

import logging, logging.handlers

from LMA_info import info

def tfromfile(name):
    parts = name.split('_')
    y, m, d = list(map(int, (parts[-3][0:2], parts[-3][2:4], parts[-3][4:6])))
    H, M, S = list(map(int, (parts[-2][0:2], parts[-2][2:4], parts[-2][4:6])))
    return y+2000,m,d,H,M,S

def sort_flashes(files, base_sort_dir, params):
    """ Given a list of LMA ASCII data files, created HDF5 flash-sorted data
        files in base_sort_dir/h5_files.

        params is a dictionary with the following format

        params = {'stations':(5,99), # range of allowable numbers of contributing stations
              'chi2':(0,25.0),    # range of allowable chi-sq values
              'distance':3000.0, 'thresh_critical_time':0.15, # space and time grouping thresholds
              'thresh_duration':3.0, # maximum expected flash duration
              'ctr_lat':38.8894, 'ctr_lon':-77.03517, #center lat/lon to use for flash sorting, gridding
              'mask_length':55, # length of the hexadecimal station mask column in the LMA ASCII files
              }

    """
    # -------------------- Setup Log File -----------------------
    # base_sort_dir = outpath
    logger_setup(base_sort_dir)
    h5_dir = os.path.join(base_sort_dir, 'h5_files')
    y,m,d,H,M,S = tfromfile(files[0])
    date = datetime(y,m,d, H,M,S)

    # ---------- Create Directory for HDF5 Files ----------------
    # Create HDF5 flash files
    base_out_dir = (h5_dir+"/20%s" %(date.strftime('%y/%m/%d')))
    if os.path.exists(base_out_dir) == False:
        os.makedirs(base_out_dir)
        subprocess.call(['chmod', 'a+w', base_out_dir, h5_dir+'/20%s' %(date.strftime('%y/%m')), h5_dir+'/20%s' %(date.strftime('%y'))])

    # ----------- Add 'tag' to directory path (?) ---------------
    tag = ''
    outdir = os.path.join(base_out_dir, tag)

    # ----------- Write 'param' settings to file ----------------
    info = open(os.path.join(outdir, 'input_params.py'), 'w')
    info.write(str(params))
    info.close()

    if True:
        # -----------------------------------------------------------
        # --------- Create Clustering Function/Object ? ? ? ? ? ? ?
        cluster = DBSCANFlashSorter(params).cluster

        # ===========================================================
        # ---------------- sort_files SubFunction -------------------
        # sort_files(files, outdir, cluster)
        # def sort_files(files, output_path, clusterer):
        files = files
        output_path = outdir
        clusterer = cluster

        # --------------------- update logs ------------------------
        logger = logging.getLogger('FlashAutorunLogger')
        now = datetime.now().strftime('Flash autosort started %Y%m%d-%H%M%S')
        logger.info(now)

        h5_outfiles = []
        for a_file in files:
            try:
                # ---------- create filename with .flash extention ----------
                file_base_name = os.path.split(a_file)[-1].replace('.gz', '')
                outfile = os.path.join(output_path, file_base_name+'.flash')

                # ===========================================================
                # *********** Create LMADataset and Cluster Data ************
                # lmadata = LMADataset(a_file,file_mask_length=params['mask_length']) (mask length param doesn't exist anymore)
                lmadata = LMADataset(a_file)
                clusterer(lmadata)

                # ----------- create filename with .h5 extention ------------
                outfile_with_extension = outfile + '.h5'
                h5_outfiles.append(outfile_with_extension)

                lmadata.write_h5_output(outfile_with_extension, a_file)
            except:
                logger.error("Did not successfully sort %s \n Error was: %s" % (a_file, sys.exc_info()[1]))
                raise
        # return h5_outfiles

        # ------------- delete subfunction variables ----------------
        del (files,output_path,clusterer,file_base_name,outfile,lmadata)
        del (outfile_with_extension,logger,now,a_file)

        # -----------------------------------------------------------
        # ===========================================================

    # ------------------------------------------------------------
    # ------------- List HDF5 files that were created ------------
    h5_filenames = glob.glob(h5_dir+'/20%s/*.dat.flash.h5' %(date.strftime('%y/%m/%d')))
    h5_filenames.sort()
    return h5_filenames

def grid(h5_filenames, base_sort_dir,
         min_points=1,
         dx=1.0e3, dy=1.0e3, dz=1.0e3,
         frame_interval=60.0,
         x_bnd=(-200.0e3, 200.0e3),
         y_bnd=(-200.0e3, 200.0e3),
         z_bnd=(0.0e3, 20.0e3),
         ctr_lat=38.5, ctr_lon=-76.3,
         center_ID='MALMA', base_date=None):
    """ Given a list of HDF5 filenames (sorted by time order) in h5_filenames,
        create 2D and 3D NetCDF grids with spacing dx, dy, dz in meters,
        frame_interval in seconds, and tuples of grid edges
        x_bnd, y_bnd, and z_bnd in meters

        The actual grids are in regular lat,lon coordinates, with spacing at the
        grid center matched to the dx, dy values given.

        Grids and plots are written to base_sort_dir/grid_files/ and  base_sort_dir/plots/
        base_date is used to optionally set a common reference time for each of the NetCDF grids.
    """
    # not really in km, just a different name to distinguish from similar variables below.
    dx_km=dx
    dy_km=dy
    x_bnd_km = x_bnd
    y_bnd_km = y_bnd
    z_bnd_km = z_bnd

    grid_dir = os.path.join(base_sort_dir, 'grid_files')
    # There are similar functions in lmatools to grid on a regular x,y grid in some map projection.
    dx, dy, x_bnd, y_bnd = dlonlat_at_grid_center(ctr_lat, ctr_lon,
                                                  dx=dx_km, dy=dy_km,
                                                  x_bnd = x_bnd_km,
                                                  y_bnd = y_bnd_km )
    for f in h5_filenames:
        y,m,d,H,M,S = tfromfile(f)
        start_time = datetime(y,m,d, H,M,S)
        end_time = start_time + timedelta(0,frame_interval)
        date = start_time
        outpath = grid_dir+'/20%s' %(date.strftime('%y/%m/%d'))
        if os.path.exists(outpath) == False:
            os.makedirs(outpath)
            subprocess.call(['chmod', 'a+w',outpath, grid_dir+'/20%s' %(date.strftime('%y/%m')), grid_dir+'/20%s' %(date.strftime('%y'))])
        if True:
            grid_h5flashfiles(h5_filenames,
                              start_time, end_time,
                              min_points_per_flash=min_points,
                              frame_interval=frame_interval,
                              proj_name='latlong',
                              base_date = base_date,
                              energy_grids='',
                              dx=dx, dy=dy,
                              x_bnd=x_bnd,
                              y_bnd=y_bnd,
                              z_bnd=z_bnd_km,
                              ctr_lon=ctr_lon,
                              ctr_lat=ctr_lat,
                              outpath = outpath,
                              output_writer = write_cf_netcdf_latlon,
                              output_writer_3d = write_cf_netcdf_3d_latlon,
                              output_filename_prefix=center_ID,
                              spatial_scale_factor=1.0)

# ===========================================================
#      ================ MAIN SCRIPT ===================
# ===========================================================
if __name__ == '__main__':

    network = sys.argv[1]
    year = sys.argv[2]
    month = sys.argv[3]
    days = sys.argv[4:]

    '''
    Directories for the HDF5 files, grids, and plots are created within the
    directory indicated by data_out

    Data files should be stored in directories by /data/year/month/day/
    '''
    for day in sorted(days):
        data_out = f'./data_lightning/www/lma_data/{network}'
        rootdir = f'{data_out}/data/{year}/{month}/{day}/'
        filenames = glob.glob(rootdir + '*.gz')
        print("Root Dir: " + rootdir)
        print("Filenames: " + str(filenames))
        lma_info = info(network)
        params = {'stations':(6,99),          # range of allowable numbers of contributing stations
                  'chi2':(0,5),               # range of allowable chi-sq values
                  'distance':3000.0,          # space grouping thresholds
                  'thresh_critical_time':0.15,# time grouping thresholds
                  'thresh_duration':3.0,      # maximum expected flash duration
                  'ctr_lat':38.5,             # center lat to use for flash sorting, gridding
                  'ctr_lon':-76.3,            # center lon to use for flash sorting, gridding
                  'mask_length':lma_info[4],  # length of hexadec station mask column in the LMA ASCII files
                  'min_points':10,            # minimum number of points per flash
                  'altitude':(0,20000)}       # range of allowable altitude

        # ------- Create List of non-empty Data Files -----------
        data_files = []
        for file in filenames:
            fname = os.path.basename(file)
            f_time = int(float((fname.split('_')[2])))
            if os.stat(file).st_size > 2048:
                data_files.append(file)
            else:
                print('file has no data')
                continue

        # -------------------------------------------------------
        # ----- Cluster Sources into Flashes (HDF5 files) -------
        h5_filenames = sort_flashes(data_files, data_out, params)

        # -------------------------------------------------------
        # ---------- Produce Gridded NetCDF files ---------------
        grid(h5_filenames, data_out,
             min_points=params['min_points'],
             dx=1.0e3, dy=1.0e3, dz=1.0e3,
             frame_interval=600,
             x_bnd=(-400.0e3, 400.0e3),
             y_bnd=(-400.0e3, 400.0e3),
             z_bnd=(0.0e3, 20.0e3),
             ctr_lat=params['ctr_lat'],
             ctr_lon=params['ctr_lon'],
             center_ID=str(network),
             base_date=datetime(2012, 1, 1))

    # ===========================================================
    #      ================ ============ ===================
    # ===========================================================
