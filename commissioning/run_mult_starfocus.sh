#!/bin/bash

BIN_STAR_FOCUS="/home/obs22/bin/runStarfocus.py"
BIN_P51="/home/obs22/bin/p_51_tiltcheck.py"
DATA_DIR="/data2/PANIC/2023-01-09-tilt"
FILTER=All
# Filter ID: (1)Ks (2)H (3)J (4)Y (5)Z (6)H2 (7)All
FILTER_ID=7

if [[ ${FILTER_ID} -eq 7 ]] 
then
	echo "We suppose is done all runStarfocus.py {1..16}"
	echo "Now, it is time to run p_51_tiltcheck.py summary for All filters "
	echo "${BIN_P51}  -i ${DATA_DIR} ${FILTER_ID}"
	${BIN_P51}  -i ${DATA_DIR} ${FILTER_ID}
else
	for i in {1..16}
	do
		echo "FILTER: ${FILTER}"
		echo "REGION file: ${DATA_DIR}/${FILTER}_Fullframe_Region_${i}.reg"
		echo "$BIN_STAR_FOCUS -s ${DATA_DIR}/${FILTER}/files_reduced.txt -c ${DATA_DIR}/${FILTER}/${FILTER}_Fullframe_Region_${i}.reg -d ${DATA_DIR}/${FILTER}_Region_${i}.txt -t ${DATA_DIR}"
		$BIN_STAR_FOCUS -s ${DATA_DIR}/${FILTER}/files_reduced.txt -c ${DATA_DIR}/${FILTER}/${FILTER}_Fullframe_Region_${i}.reg -d ${DATA_DIR}/${FILTER}_Region_${i}.txt -t ${DATA_DIR}
	done

	echo "Done all runStarfocus.py {1..16}"
	echo "Now, it is time to run p_51_tiltcheck.py ..."
	echo "${BIN_P51}  -i ${DATA_DIR} ${FILTER_ID}"
	${BIN_P51}  -i ${DATA_DIR} ${FILTER_ID}
fi
