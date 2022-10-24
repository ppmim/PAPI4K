DEST=/tmp
PAPI_DIR=../papi/
now=`date +"%Y%m%d-%H%M%S"`
cd $PAPI_DIR
git archive --format zip --output $DEST/papi_$now.zip master
