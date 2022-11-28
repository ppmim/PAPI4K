#!/bin/bash

BIN_STAR_FOCUS = /home/obs22/bin/runStarfocus.py
BIN_P51 = /home/obs22/bin/p_51_tiltcheck.py
OBJ_NAME = m_obj
FILTER = Ks
# Filter ID: (1)Ks (2)H (3)J (4)Y (5)Z (6)H2 (7)All
FILTER_ID = 1

for i in {1 .. 16}
do
	echo "FILTER: ${FILTER}"
	echo "REGION file: ${OBJ_NAME}/${FILTER}_Region_$i.reg" 
	$BIN_STAR_FOCUS -s ${OBJ_NAME}/${FILTER}/files_reduced.txt -c ${OBJ_NAME}/${FILTER}_Region_$i.reg -d ${OBJ_NAME}/${FILTER}_Region_$i.txt -t ${OBJ_NAME}
done

echo "Done all runStarfocus.py {1..16}"
echo "Now, it is time to run p_51_tiltcheck.py ..."
${BIN_P51}  -i ${OBJ_NAME} ${FILTER_ID}