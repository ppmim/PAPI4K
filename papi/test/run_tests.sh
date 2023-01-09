# Scripts to run PAPI tests

#
python run_papi.py -c config_files/papi.cfg -s /opt/PANIC_DATA/SIMU_4k/sci_H/Q1/scaled/ -S 0 0
python run_papi.py -c config_files/papi.cfg -s /opt/PANIC_DATA/2015-03-10/ -S 11 11
python run_papi.py -c config_files/papi_o2k.cfg -s /opt/PANIC_DATA/20120105_O2K  -d /opt/PANIC_DATA/out/ -S 48 48 -t /opt/PANIC_DATA/tmp/
# 
python reduce/calDark.py -s /opt/PANIC_DATA/PAPI_TEST/dark_seq.txt -o /tmp/masterDark.fits
python reduce/calTwFlat.py -s /opt/PANIC_DATA/PAPI_TEST/sky_ff_seq.txt -D /tmp/prueba.fits -o /tmp/masteTW_FF.fits
python reduce/calDomeFlat.py -s /opt/PANIC_DATA/PAPI_TEST/dome_seq.txt -o /tmp/master_DOME_FF.fit
python reduce/calGainMap.py -s /tmp/master_DOME_FF.fits -o /tmp/gainMap.fits
modhead /tmp/master_DOME_FF_H.fits filter H
python reduce/applyDarkFlat.py -s /opt/PANIC_DATA/SIMU_4k/sci_H/Q1/scaled/simu_sci_H_4k.txt -d /opt/PANIC_DATA/PAPI_TEST/DARK_MODEL/masterDM.fits -f /tmp/master_DOME_FF_H.fits
python reduce/calBPM_2.py -s /opt/PANIC_DATA/PAPI_TEST/dome_seq.txt -D /tmp/masterDark_2_1.fits
python reduce/calBPM_3.py -d /opt/PANIC_DATA/PAPI_TEST/dark_seq.txt -f /opt/PANIC_DATA/PAPI_TEST/dome_seq.txt -o /tmp/bpm.fits
python reduce/skySubtraction.py  -i /opt/PANIC_DATA/SIMU_4k/sci_H/Q1/scaled/simu_sci_H_4k.txt -c ../config_files/papi.cfg -o /tmp/
python reduce/montage.py -l /opt/PANIC_DATA/SIMU_4k/sci_H/Q1/scaled/simu_sci_H_4k.txt

#
python reduce/solveAstrometry.py -s /opt/PANIC_DATA/focus_0024.fits



# panic22 / panic35

python reduce/solveAstrometry.py -s /data1/PANIC/SIMU_4k/sci_H/Q1/scaled/Standard_Star_FS15_March10_0026.Q01_coadd_scaled.fits
python run_papi.py -c config_files/papi.cfg -s /data1/PANIC/SIMU_4k/sci_H/Q1/scaled/ -S 0 0 -d /data2/out/  -t /data2/tmp/
python reduce/montage.py -l /data1/PANIC/SIMU_4k/sci_H/Q1/scaled/simu_sci_H_4k.txt
python run_papi.py -c config_files/papi.cfg -s /data1/PANIC/2015-06-24/ -S 67 67  -d /data2/out/ -t /data2/tmp/
python run_papi.py -c config_files/papi.cfg -s /data1/PANIC/2015-06-24/ -S 36 36  -d /data2/out/ -t /data2/tmp


# Processing in panic22:

# To create master DarkModel
python reduce/calDarkModel.py  -s /data2/tmp/dark_model_files_28dic.txt  -o /data2/tmp/DM2.fits

# To create master TW flats
python reduce/calTwFlat.py  -s /data2/tmp/tw_flats_H.txt  -D /data1/Calibs2/DarkModel_CNTSR.fits -o /data2/tmp/Master_TW_Flat_H.fits -N