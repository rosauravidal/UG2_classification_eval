from keras.applications.resnet50 import ResNet50
from keras.applications.vgg16 import VGG16
from keras.applications.vgg19 import VGG19
from keras.applications.inception_v3 import InceptionV3
from keras.applications.inception_v3 import preprocess_input as inception_preprocess_input
from keras.applications.imagenet_utils import preprocess_input, decode_predictions
from keras.preprocessing import image

import numpy as np
import pandas as pd
from tqdm import tqdm
import sys
import os

# To run:
# Format:	python imgClassification.py path/to/input/ path/to/input_classes.txt path/to/UG2ImageNetEquivalencies.txt path/to/output.txt
# Example:	python imgClassification.py SampleInput/ sampleInput_Eqs.txt UG2ImageNet.txt scores.txt

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # remove tensorflow verbose

NPREDS = 5 #number of predictions to be generated by each model

inputTypes = ('.jpeg', '.jpg', '.tiff', '.tif', '.png')
# Preprocesses images for each model's specifications
# returns the resized image
def preprocessImg(imgPath, isInception=False):
	img = image.load_img(imgPath)
	if isInception:
		img = img.resize((299,299))
		img = image.img_to_array(img)
		img = np.expand_dims(img, axis=0)
		img = inception_preprocess_input(img)
	else:
		size=(224,224)
		img = image.load_img(imgPath, target_size=size)
		img = image.img_to_array(img)
		img = np.expand_dims(img, axis=0)
		img = preprocess_input(img)
	return img

# Processes imagenet classes predictions and calculates classification accuracy for ug2 classes
# returns M1, M2 
# M1: rate in which the at least one of the class predictions in the top5 predictions of the network is correct
# M2: rate in which the all of the possible class predictions are found in the top5 predictions of the network
def processPredictions (modelPredictions, modelName):
	M1 = 0.0 # Metric 1: At least 1 correct classification in top 5
	M2 = 0.0 # Metric 2: Found all possible correct classes in the top 5

	for imgPredictions in tqdm(modelPredictions):
		iName = os.path.splitext(imgPredictions[0])[0]
		top5Preds = imgPredictions[1]
		imgUG2Class = trueClasses[trueClasses.ImageName == iName]['UG2Class'].tolist()[0] # the class annotated for the image

		# get the number of imagenet classes that form part of the image's ug2 superclass
		maxPossibleClasses = len(ug2INetEqs[ug2INetEqs.UG2Class == imgUG2Class])
		# if the number of subclasses is higher that the number of predictions we obtained, the maximum number of correct classes would be the number of predictions we obtained
		if maxPossibleClasses > NPREDS: 
			maxPossibleClasses = NPREDS

		iNetIDs = [pred[0] for pred in top5Preds]
		correctClasses = ug2INetEqs[(ug2INetEqs.ID.isin(iNetIDs)) & (ug2INetEqs.UG2Class == imgUG2Class)]

		if len(correctClasses) > 0:
			M1 += 1
			if len(correctClasses) == maxPossibleClasses:
				M2 += 1

	M1_rate = M1 / len(modelPredictions)
	M2_rate = M2 / len(modelPredictions)
	print modelName, 'scores:'
	print '\tM1:', M1_rate
	print '\tM2:', M2_rate

	return M1_rate, M2_rate


imgsFolder = os.path.abspath(sys.argv[1])
inputClasses = os.path.abspath(sys.argv[2])
ug2INetEqsPath = os.path.abspath(sys.argv[3])
scoresPath = os.path.abspath(sys.argv[4])



imgNameList = [f for f in os.listdir(imgsFolder) if f.endswith(inputTypes)]

print '________________________________________'
print 'Input images:', imgsFolder, '(found', len(imgNameList), 'images)'
print 'List of image classes:', inputClasses
print 'UG2-ImageNet classes equivalencies:', ug2INetEqsPath
print 'Ouput scores location:', scoresPath

print '________________________________________'
print 'Instantiating models...'
models = {}

print('\tResNet')
models['ResNet'] = ResNet50(weights='imagenet') 
print('\tVGG16')
models['VGG16'] = VGG16(weights='imagenet')
print('\tVGG19')
models['VGG19'] = VGG19(weights='imagenet')
print('\tInception')
models['Inception'] = InceptionV3(weights='imagenet')

print '________________________________________'
print 'Loading UG2-ImageNet classes equivalencies'
ug2INetEqs = pd.read_csv(ug2INetEqsPath, names=['ID', 'UG2Class', 'INetDesc'], sep='\t')
trueClasses = pd.read_csv(inputClasses, names=['ImageName', 'UG2Class'], sep='\t')

print '________________________________________'
print 'Preprocessing images (resizing for networks)'
images = []
for imgName in tqdm(imgNameList):
	img = preprocessImg(os.path.join(imgsFolder, imgName))
	images.append(img)
inceptionImages = []
for imgName in tqdm(imgNameList):
	img = preprocessImg(os.path.join(imgsFolder, imgName), isInception=True)
	inceptionImages.append(img)

print '________________________________________'
print 'Image classification'

modelScores = []

for mName, model in models.iteritems():
	print '\nModel:', mName
	modelPredictions = [] # imageName, [['id1', confidence2], ['id2', confidence2], ..., ['id5', confidence5]]
	
	if mName == 'Inception':
		predImages = inceptionImages
	else:
		predImages = images
	print 'ImageNet classification'
	for i in tqdm(range(len(predImages))):
		predictions = model.predict(predImages[i])
		decoded = sorted([[d[0], d[2]] for d in decode_predictions(predictions,top=NPREDS)[0]],key=lambda x: x[1],reverse=True)
		modelPredictions.append([imgNameList[i],decoded])

	print 'Preprocessing classification results'
	M1, M2 = processPredictions(modelPredictions, mName)
	modelScores.append([mName, M1,  M2])

print '________________________________________'
print 'Model Scores:'

output = 'Model\tM1\tM2\n'
output += '\n'.join(['\t'.join([score[0],str(score[1]),str(score[2])]) for score in modelScores])
	
print output

with open(scoresPath, 'w+') as f:
	f.write(output)