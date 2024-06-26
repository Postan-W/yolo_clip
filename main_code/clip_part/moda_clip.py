# require modelscope>=0.3.7，目前默认已经超过，您检查一下即可
# 按照更新镜像的方法处理或者下面的方法
# pip install --upgrade modelscope -f https://modelscope.oss-cn-beijing.aliyuncs.com/releases/repo.html
# 需要单独安装decord，安装方法：
"""
modelscope
decord
timm
librosa
fairseq 会安装torch
"""
import torch
from modelscope.utils.constant import Tasks
from modelscope.pipelines import pipeline
from modelscope.preprocessors.image import load_image
from ultralytics import YOLO
import numpy as np
import os
os.environ['MODELSCOPE_CACHE'] = "../models/"#指定模型存放地点
from PIL import Image
import cv2
pipeline = pipeline(task=Tasks.multi_modal_embedding,
    model='damo/multi-modal_clip-vit-large-patch14_336_zh', model_revision='v1.0.1')

def local_img():
    input_img = load_image("../clip_images/image030.jpg")
    # 支持皮卡丘示例图片路径/本地图片 返回PIL.Image
    input_texts = ["有人在弯腰翻越障碍物", "有人双手支撑在障碍物上攀爬", "有人笔直地站着", "人笔直通过障碍物",
                   "有人从障碍物旁边走过", "画面里没有人"]

    # 支持一张图片(PIL.Image)或多张图片(List[PIL.Image])输入，输出归一化特征向量
    img_embedding = pipeline.forward({'img': input_img})['img_embedding']

    # 支持一条文本(str)或多条文本(List[str])输入，输出归一化特征向量
    text_embedding = pipeline.forward({'text': input_texts})['text_embedding']

    # 计算图文相似度
    with torch.no_grad():
        # 计算内积得到logit，考虑模型temperature
        logits_per_image = (img_embedding / pipeline.model.temperature) @ text_embedding.t()
        # 根据logit计算概率分布
        probs = logits_per_image.softmax(dim=-1).cpu().numpy()
    clean_result = []
    for img_result in probs:
        clean_result.append([round(i, 2) for i in img_result])
    print("图文匹配概率:", clean_result)


def crop_by_ultralytics(image_path,model_path,input_texts,target_texts,classes,conf):
    yolo_model = YOLO(model_path)
    result = yolo_model(image_path, save=True,classes=classes,conf=conf)[0]
    boxes = result.boxes.data.tolist()#[[x1,y1,x2,y2,id,conf,]]
    print("初始:boxes:{}".format(boxes))
    if not len(boxes) == 0:
        final_boxes = []
        origin_frame = result.orig_img
        frame_height,frame_width,_ = origin_frame.shape
        #hwc
        padding_y = int(frame_height/10)#box高度增加1/5
        padding_x = int(frame_width/10)#box宽度增加1/5
        clip_input = []
        for box in boxes:
            x1, y1, x2, y2 = int(box[0]), int(box[1]), int(box[2]), int(box[3])
            x1 = x1 - padding_x if (x1 - padding_x) > 0 else 0
            y1 = y1 - padding_y if (y1 - padding_y) > 0 else 0
            x2 = x2 + padding_x if (x2 + padding_x) < frame_width else frame_width
            y2 = y2 + padding_y if (y2 + padding_y) < frame_height else frame_height
            croped = origin_frame[y1:y2, x1:x2, :]
            rgb_image = cv2.cvtColor(croped, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_image)
            clip_input.append(pil_image)
            pil_image.show()



        # 支持一张图片(PIL.Image)或多张图片(List[PIL.Image])输入，输出归一化特征向量
        img_embedding = pipeline.forward({'img': clip_input})['img_embedding'] #2D Tensor, [图片数, 特征维度]

        #这句话在正式代码中放最外层
        # 支持一条文本(str)或多条文本(List[str])输入，输出归一化特征向量
        text_embedding = pipeline.forward({'text': input_texts})['text_embedding']

        # 计算图文相似度
        with torch.no_grad():
            # 计算内积得到logit，考虑模型temperature
            logits_per_image = (img_embedding / pipeline.model.temperature) @ text_embedding.t()
            # 根据logit计算概率分布
            probs = logits_per_image.softmax(dim=-1).cpu().numpy()
        clean_result = []
        for img_result in probs:
            clean_result.append([round(i, 2) for i in img_result])
        # print("图文匹配概率:", clean_result)
        for i,prob in enumerate(clean_result):
            # print(i,prob)
            result_dict = {}
            for j,p in enumerate(prob):
                result_dict[p] = input_texts[j]
            print(result_dict)
            target_prob = sum(prob[:target_texts])
            residual_prob = sum(prob[target_texts:])
            print(target_prob,residual_prob)
            if target_prob > residual_prob:
                final_boxes.append(list(boxes[i]))

        print("final boxes:{}".format(final_boxes))



input_texts_climb = ["有人在弯腰翻越障碍物", "有人双手支撑在障碍物上攀爬","有人支撑在障碍物上跳跃","有人拿着衣服走过通道", "人的腿被障碍物完全挡住了","有人笔直地站着", "人笔直通过障碍物",
                   "有人从障碍物旁边走过", "画面里没有人","人的手没有触碰障碍物"]
input_texts_fall = ["有人躺在地上", "有人摔倒在地上","有人躺在地上睡觉","有人在楼梯上摔倒了","有人在手扶电梯上摔倒了","有人在上楼梯","有人在下楼梯","有人站在手扶电梯上","有人站在楼梯上","有人蹲在手扶电梯上","有人蹲在楼梯上","有人坐在手扶电梯上","有人坐在楼梯上","有人坐在地上","有人坐在椅子上","画面里没有人", "鞋子在地上",
                   "箱子在地上", "毯子在地上","一块布在地上","画面里有个物体不是人","有人在行走","有人在站着","有人在蹲着","有人在蹲着玩手机","有人在修理东西"]
input_texts_fall2 = ["有人躺在地上", "有人摔倒在地上","有人躺在地上睡觉","有人在楼梯上摔倒了","有人在手扶电梯上摔倒了","有人在上楼梯","有人在下楼梯","有人站在手扶电梯上","有人站在楼梯上","有人蹲在手扶电梯上","有人蹲在楼梯上","有人坐在手扶电梯上","有人坐在楼梯上","有人坐在地上","有人坐在椅子上","画面里没有人", "鞋子在地上",
                   "箱子在地上", "毯子在地上","一块布在地上","画面漆黑没有人","有人在行走","有人在站着","有人在蹲着","有人在蹲着玩手机","有人在修理东西"]
target_texts_climb = 3
target_texts_fall = 5
crop_by_ultralytics(image_path="../clip_images/shuaidao_wubao2.png",model_path="../weights/fall_yolov8l_20240626.engine",input_texts=input_texts_fall,target_texts=target_texts_fall,classes=[3],conf=0.75)
# crop_by_ultralytics(image_path="../clip_images/climb_wubao_2.jpg",model_path="../weights/climb_yolov8l_80epoch_batch64_old_data_20240625.pt",input_texts=input_texts_climb,target_texts=target_texts_climb,classes=[1],conf=0.25)
