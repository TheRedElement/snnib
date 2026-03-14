# for publication (creates installable blender add-on from src/pkg/ directory structure)

#create installable blender add-on
cd ./src/
zip -r ../snnib.zip snnib
cd -

#generate animations (mkv -> gif; compress gif)
ffmpeg -i ./renders/SnnibBrian2Tiny0001-0120.mkv ./renders/SnnibBrian2Tiny0001-0120.gif
ffmpeg -i ./renders/SnnibBrian2Tiny0001-0120.gif -filter_complex "scale=480:-1" ./renders/_SnnibBrian2Tiny0001-0120.gif #temporary to avoid write conflicts
mv ./renders/_SnnibBrian2Tiny0001-0120.gif ./renders/SnnibBrian2Tiny0001-0120.gif
ffmpeg -i ./renders/SnnibRandom0001-0120.mkv ./renders/SnnibRandom0001-0120.gif
ffmpeg -i ./renders/SnnibRandom0001-0120.gif -filter_complex "scale=480:-1" ./renders/_SnnibRandom0001-0120.gif         #temporary to avoid write conflicts
mv ./renders/_SnnibRandom0001-0120.gif ./renders/SnnibRandom0001-0120.gif
