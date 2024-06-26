import cv2
import os

def get_source(rootpath:str,source_format:list=["mp4"]):
    source_list = [i for i in os.listdir(rootpath) if i.split(".")[1] in source_format]
    return [os.path.join(rootpath,i) for i in source_list]

def get_images(videopath,destination,step = 5,current_video_index=0,total_video_num=None):
    if not os.path.exists(destination):
        os.makedirs(destination)

    video_name = os.path.splitext(os.path.split(videopath)[1])[0]
    cap = cv2.VideoCapture(videopath)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    # print(cap.get(cv2.CAP_PROP_FPS))
    ret, frame = cap.read()
    count = 1
    while ret:
        if count % step == 0 and ret:
            filename = os.path.join(destination, video_name + "_" + str(count) + ".jpg")
            cv2.imwrite(filename, frame)
        print("总:{}/{}; 当前视频处理进度:{}/{},{}%".format(current_video_index,total_video_num,count, total_frames, round((count / total_frames) * 100, 2)))
        ret, frame = cap.read()
        count += 1
    cap.release()
    cv2.destroyAllWindows()


destination = "C:/Users/wmingdru/Desktop/workspace/data/temp_material/train_val/val/images/"
videos = get_source("C:/Users/wmingdru/Desktop/workspace/data/temp_material/val_videos/")

total_video_num = len(videos)
for i,videopath in enumerate(videos):
    get_images(videopath,destination,step=15,current_video_index=i+1,total_video_num=total_video_num)


def single_video():
    cap = cv2.VideoCapture("videos/fanyue/new_fanyue.avi")
    ret, frame = cap.read()
    destination = "C:/Users/wmingdru/Desktop/new_fanyue"
    count = 1
    while ret:
        if count % 2 == 0 and ret:
            filename = os.path.join(destination, "new_fanyue" + "_" + str(count) + ".jpg")
            cv2.imwrite(filename, frame)
        ret, frame = cap.read()
        count += 1
    cap.release()
    cv2.destroyAllWindows()