DEST_BLOG="src/posts_old"
DEST_IMAGES="src/images"


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
        dest=`echo "${DEST_IMAGES}/${name}.png"`
        cp -p ${2} ${dest}
        echo "Generation of ${dest}"
        mogrify -crop  ${h}x${w}+${left}+${top} +repage ${dest}
    done < "$1"

}

# #---- Blog posts and images

# mv ${DEST_BLOG}/posts.json src
# rclone sync dev:BLOG_POSTS ${DEST_BLOG}
# mv src/posts.json ${DEST_BLOG}
# mv ${DEST_BLOG}/images/* ${DEST_IMAGES}

#----- Images from slides
if [ -d tmp_slides ] ; then
    rm -rf tmp_slides
fi
mkdir tmp_slides
rclone sync dev:SLIDES_COMPIL tmp_slides

for fic in `find tmp_slides -name "*.txt"`
do
    img=${fic%.*}.png
    generateImages $fic $img
done


#rm -rf tmp_slides



