DEST=/tmp
PAPI_DIR=../
now=`date +"%Y%m%d-%H%M%S"`
cd $PAPI_DIR
git archive --format zip --output $DEST/papi_$now.zip master papi

echo $DEST/papi_$now.zip 

echo "Copying to panic22 and panic35...."
rsync -av $DEST/papi_$now.zip panic@panic22.caha.es:/data1/ICS/QL_INSTALL/PAPI22
rsync -av $DEST/papi_$now.zip panic@panic35.caha.es:/data1/ICS/QL_INSTALL/PAPI22
