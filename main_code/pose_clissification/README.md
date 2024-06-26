# 1.introduction

```
使用检测+追踪+关键点检测,然后利用拿到的关键点，送入到一个分类模型(可以是一个简单的dense分类模型)进行动作分类
参见https://github.com/Postan-W/YoloV8-Pose-Keypoint-Classification
```

```
也可以检测模型就用检测各种动作的yolo，用姿势检测模型再对crop的目标检测姿势，然后进行分类
```



## **要做的工作如下：**

- 标注目标检测样本，标注的对象就是人体，然后分为几类，包括站立、弯腰、蹲下、翻越、坐着等，训练一个目标检测模型。
- 利用人体关键点检测模型检测得到各种动作的关键点数据；
- 将上述得到的关键点数据组织成结构化数据，并打上动作类别标签；
- 构建多分类模型；
- 训练模型；
- 将训练得到的模型用于目标检测和追踪的下一步，即对检测到的人的关键点进行分类。

## **"训练数据的构造方法"**

和翻越闸机或者摔倒的模型一样，训练一个分类多个人体动作的yolo,然后用测试视频跑出结果，然后仔细查看结果中有没有分类错误的情形，如果没有的话，就可以根据每个box的cls来保存关键点和其标签了。

上面的构造数据的方法行不通，因为目标检测模型检测出来的动作和关键点检测模型检测出的关键点无法找到一个合适的方法将其对应上。

**新思路**

用姿势检测模型推理视频，每一帧的结果的n个box，每次plot一个，然后程序等待我输入一个动作类别，然后将对应的关键点数据和类别写入文件的一行(比如一个.txt)，这样整个视频跑完我就能得到一份训练数据了。要注意的每次plot当前box的时候，之前的box不能存在，不然无法得知当前的box是哪个，当然也有解决办法，就是给box编号，1到当前帧的box数量，于是每次plot的box就是当前编号最大的那个。cv2.imshow时标题设为当前box的index，也能起到提示作用。	

如果能写成一个UI就更好了。

