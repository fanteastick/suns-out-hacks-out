from emotions import FilterEmotions, emotion_mapping
from filter_pos import *

if __name__ == '__main__':
    single_face_image_url = 'https://encrypted-tbn0.gstatic.com/images?q=tbn%3AANd9GcRfkrYgTxf2uCXFHxi7t2QUIaefqfcpsm-jGg&usqp=CAU'
    ffilt = faceFilter()
    # img = ffilt.addFilterURL(single_face_image_url, 0, 0)
    path_pics = pathlib.Path().cwd() / "pictures"
    list_of_pics = glob.glob(os.path.join(path_pics, '*'))
    image_list = []
    for pic in list_of_pics:
        image_list.append(pic)
    img = cv2.imread(image_list[2])
    print('cv2 read image type: ', type(img))
    img = ffilt.addFilter(img, 0, 0)
    print('converted filter image type: ', type(img))
    cv2.imshow('image with filter', img)
    cv2.waitKey(0)