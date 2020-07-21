SOURCE_DOCS="/mnt/chromeos/GoogleDrive/MyDrive/dev/DOC_COMPIL/"
RAC="/home/laurent/dev/aurora2.0"
DEST_DOCS="${RAC}/src/"
SOURCE_SLIDES="/mnt/chromeos/GoogleDrive/MyDrive/dev/SLIDES_COMPIL/"
DEST_SLIDES="${RAC}/src/images/"


generateImages() {

  while IFS= read -r line
  do
    #echo $line
    IFS='|' tokens=( $line )
    name=`echo  "${tokens[0]}"`
    left=`echo "${tokens[1]}"`
    top=`echo "${tokens[2]}"`
    h=`echo "${tokens[3]}"`
    w=`echo "${tokens[4]}"`

    dir=`dirname $2`
    dest=`echo "${RAC}/_site/images/${name}.png"`
    cp -p ${2} ${dest}
    echo "Generation of ${dest}"
    mogrify -crop  ${h}x${w}+${left}+${top} +repage ${dest}
  done < "$1"

}

LOCK=`find $SOURCE_DOCS -name todo|wc -l`
if [ $LOCK -gt 0 ]
then
  echo `date`" Start - - - - "
  rm ${SOURCE_DOCS}/todo*
  touch ${SOURCE_DOCS}/inprogress
  #rm -rf ${DEST_DOCS}/*
  cp -ra ${SOURCE_DOCS}/* $DEST_DOCS
  #rm -rf ${DEST_SLIDES}/*
  cp -ra ${SOURCE_SLIDES}/* $DEST_SLIDES
  for fic in `find ${RAC}/_site/images/ -name "*.txt"`
  do
    img=${fic%.*}.png
    generateImages $fic $img
  done

    mv ${SOURCE_DOCS}/inprogress ${SOURCE_DOCS}/done
    rm ${DEST_DOCS}/inprogress
  echo `date`" Finish - - - - "
fi