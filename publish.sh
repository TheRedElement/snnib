# for publication (creates installable blender add-on from src/pkg/ directory structure)

# #create installable blender add-on
# cd ./src/
# zip -r ../releases/snnib.zip snnib
# cd -

# #generate animations (mkv -> gif; compress gif)
# ffmpeg -i ./renders/SnnibBrian2Small0001-0120.mkv ./renders/SnnibBrian2Small0001-0120.gif
# ffmpeg -i ./renders/SnnibBrian2Small0001-0120.gif -filter_complex "scale=480:-1" ./renders/_SnnibBrian2Small0001-0120.gif #temporary to avoid write conflicts
# mv ./renders/_SnnibBrian2Small0001-0120.gif ./renders/SnnibBrian2Small0001-0120.gif
# exit
# ffmpeg -i ./renders/SnnibBrian2Tiny0001-0120.mkv ./renders/SnnibBrian2Tiny0001-0120.gif
# ffmpeg -i ./renders/SnnibBrian2Tiny0001-0120.gif -filter_complex "scale=480:-1" ./renders/_SnnibBrian2Tiny0001-0120.gif #temporary to avoid write conflicts
# mv ./renders/_SnnibBrian2Tiny0001-0120.gif ./renders/SnnibBrian2Tiny0001-0120.gif

# ffmpeg -i ./renders/SnnibCustom0001-0120.mkv ./renders/SnnibCustom0001-0120.gif
# ffmpeg -i ./renders/SnnibCustom0001-0120.gif -filter_complex "scale=480:-1" ./renders/_SnnibCustom0001-0120.gif         #temporary to avoid write conflicts
# mv ./renders/_SnnibCustom0001-0120.gif ./renders/SnnibCustom0001-0120.gif

# ffmpeg -i ./renders/SnnibRandom0001-0120.mkv ./renders/SnnibRandom0001-0120.gif
# ffmpeg -i ./renders/SnnibRandom0001-0120.gif -filter_complex "scale=480:-1" ./renders/_SnnibRandom0001-0120.gif         #temporary to avoid write conflicts
# mv ./renders/_SnnibRandom0001-0120.gif ./renders/SnnibRandom0001-0120.gif

#adjust screen recordings
ffmpeg -i ./gfx/SnnibTutorialUiRandom.webm ./gfx/SnnibTutorialUiRandom.gif
ffmpeg -i ./gfx/SnnibTutorialUiRandom.webm ./gfx/SnnibTutorialFromFile.gif
ffmpeg -i ./gfx/SnnibTutorialUiRandom.webm ./gfx/SnnibTutorialGeoNodes.gif
