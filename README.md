# UG2_classification_eval
Evaluation of the classification performance of  VGG16, VGG19, ResNet and Inception on the [UG2 Dataset](http://www.ug2challenge.org/dataset.html)

## How to run:
Format:	
```
  python imgClassification.py path/to/input/ path/to/input_classes.txt path/to/UG2ImageNetEquivalencies.txt path/to/output.txt
```
Example:	
```
  python imgClassification.py SampleInput/ sampleInput_Eqs.txt UG2ImageNet.txt scores.txt
```
## Description of the inputs:
### **SampleInput/**
Folder containing the images to be evaluated. **For the [UG2Challenge](http://www.ug2challenge.org/) we only accept images of types: '.jpeg', '.jpg', '.tiff', '.tif', or '.png'**, however for any other application feel free to modify the inputTypes to what fits your needs.

### **sampleInput_Eqs.txt**
This file contains the "ground truth" to be used to determine whether the algorithms classified each image correctly. Each line contains the image name and its class (separated by a tab). It must contain one line per image contained in the input folder. You can edit this file to add the name of your own images.
For example:
```
Bic_bicycle_60_na_cloudy_gopro_0_33	Bicycle
Bicycle_bicycle_60_na_cloudy_gopro_0_33	Bicycle
Car_AV00020_2_1689	Car1
Car1_AV00020_2_1689	Car1
```
### **UG2ImageNet.txt**
Given that for some of the images in the UG2 Dataset it is impossible to provide finegrained annotations (for example, it might be impossible to know what type of car is shown by an image taken from a glider) we introduced a group of super-classes that are conformed by a group of ILSVRC synsets (e.g. the UG2 super-class Aircraft is composed by the ILSVRC synsets: n02690373 -airliner-, n04266014 -space shuttle-, etc.). 
This file contains the equivalencies between ILSVRC classes an UG2 super-classes. Each row contains three elements, the ImageNet synset ID, the equivalent UG2-super class, and the ImageNet description of the synset:
```
ID	UG2Class	INetDesc
n02690373	Aircraft	airliner
n04266014	Aircraft	space shuttle
n04552348	Aircraft	warplane, military plane
```
## Description of the output file:
imgClassification.py will obtain the top 5 predictions for each of the images in the input folder with the [pre-trained networks](https://keras.io/applications/) VGG16, VGG19, ResNet50, and InceptionV3. It will then evaluate the classification of this networks using the UG2 superclasses and will then return the scores of each network for the two metrics described in our [paper](https://arxiv.org/abs/1710.02909):
- **M1**: Rate of detection of at least 1 correctly classified synset class. In other words, for a super-class label (Li = {s1, ..., sn}), a network is able to detect 1 or more correctly classified synsets in the top 5 predictions. 
- **M2**: Rate of detecting all the possible correct synset classes in the super-class label synset set. For example, for a super-class label (Li = {s1, s2, s3}), a network is able to detect 3 correct synsets in the top 5 labels.
