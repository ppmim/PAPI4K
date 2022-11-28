#!/bin/bash

BIN_STAR_FOCUS="/home/jmiguel/bin/runStarfocus.py"
BIN_P51="/home/jmiguel/bin/p_51_tiltcheck.py"
OBJ_NAME=my_obj
FILTER=Ks
# Filter ID: (1)Ks (2)H (3)J (4)Y (5)Z (6)H2 (7)All
FILTER_ID=1

for i in {1..3}
do
	echo "FILTER: ${FILTER}"
	echo "REGION file: ${OBJ_NAME}/${FILTER}_Region_${i}.reg"
        echo "$BIN_STAR_FOCUS -s ${OBJ_NAME}/${FILTER}/files_reduced.txt -c ${OBJ_NAME}/${FILTER}_Region_${i}.reg -d ${OBJ_NAME}/${FILTER}_Region_${i}.txt -t ${OBJ_NAME}" 
	$BIN_STAR_FOCUS -s ${OBJ_NAME}/${FILTER}/files_reduced.txt -c ${OBJ_NAME}/${FILTER}_Region_${i}.reg -d ${OBJ_NAME}/${FILTER}_Region_${i}.txt -t ${OBJ_NAME}
done

echo "Done all runStarfocus.py {1..16}"
echo "Now, it is time to run p_51_tiltcheck.py ..."
echo "${BIN_P51}  -i ${OBJ_NAME} ${FILTER_ID}"
${BIN_P51}  -i ${OBJ_NAME} ${FILTER_ID}
