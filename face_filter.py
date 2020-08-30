from emotions import FilterEmotions, emotion_mapping
from filter_pos import *

single_face_image_url = 'https://encrypted-tbn0.gstatic.com/images?q=tbn%3AANd9GcRfkrYgTxf2uCXFHxi7t2QUIaefqfcpsm-jGg&usqp=CAU'
ffilt = faceFilter()
# img = ffilt.addFilterURL(single_face_image_url, 0, 0)
path_pics = pathlib.Path().cwd() / "pictures"
list_of_pics = glob.glob(os.path.join(path_pics, '*'))
image_list = []
for pic in list_of_pics:
    image_list.append(pic)
img = cv2.imread(image_list[2])
img = ffilt.addFilter(img, 0, 0)
img.show()
