# -*- coding: utf-8 -*-
"""super-resolution-u-net.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/11zT6b31dX8xaWlYNn5vA0tumON4EIyqR
"""

import os
import re
from scipy import ndimage, misc
from tqdm import tqdm
from tensorflow.keras.preprocessing.image import img_to_array


from skimage.transform import resize, rescale
import matplotlib.pyplot as plt
import numpy as np
np. random. seed(0)
import cv2 as cv2

import tensorflow as tf
from tensorflow.keras.layers import Input, Dense ,Conv2D,MaxPooling2D ,Dropout, Activation
from tensorflow.keras.layers import Conv2DTranspose, UpSampling2D, add
from tensorflow.keras.models import Model
from tensorflow.keras import regularizers
from tensorflow.keras.utils import plot_model
import tensorflow as tf

print(tf.__version__)

from google.colab import drive
drive.mount('/content/drive')

#first image to be provided as input.

# Directory containing your image files
image_dir = "/content/drive/MyDrive/Colab Notebooks/data/sandstone/128_patches/images"

# List all image files in the directory
image_files = [f for f in os.listdir(image_dir) if f.endswith('.png')]

# Define the desired image size (SIZE_X and SIZE_Y)
SIZE_X = 256
SIZE_Y = 256

# Initialize an empty list to store image data
img_data = []

# Iterate through the image files, load, convert, and resize them
for image_file in image_files:
    img_path = os.path.join(image_dir, image_file)
    img = cv2.imread(img_path, 1)  # Change 1 to 0 for grayscale images
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (SIZE_X, SIZE_Y))

    # Append the resized image to the list
    img_data.append(img)

# Convert the list of images to a numpy array
img_array = np.array(img_data)

# Normalize the image data to values between 0 and 1
low_img = img_array.astype('float32') / 255.0

#Second image to be provided as ground truth.

# Directory containing your image files
image_dir1 = "/content/drive/MyDrive/Colab Notebooks/data/sandstone/128_patches/masks"

# List all image files in the directory
image_files1 = [f for f in os.listdir(image_dir1) if f.endswith('.png')]

# Define the desired image size (SIZE_X and SIZE_Y)
SIZE_X = 256
SIZE_Y = 256
SIZE = 256
# Initialize an empty list to store image data
img_data2 = []

# Iterate through the image files, load, convert, and resize them
for image_file1 in image_files1:
    img_path1 = os.path.join(image_dir1, image_file1)
    img2 = cv2.imread(img_path1, 1)  # Change 1 to 0 for grayscale images
    img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)
    img2 = cv2.resize(img2, (SIZE_X, SIZE_Y))

    # Append the resized image to the list
    img_data2.append(img2)

# Convert the list of images to a numpy array
img_array2 = np.array(img_data2)

# Normalize the image data to values between 0 and 1
high_img = img_array2.astype('float32') / 255.0

# # to get the files in proper order

# import re

# def sorted_alphanumeric(data):
#     convert = lambda text: int(text) if text.isdigit() else text.lower()
#     alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
#     return sorted(data, key=alphanum_key)


# # defining the size of the image
# SIZE = 256
# high_img = []
# path = "/content/drive/MyDrive/Colab Notebooks/data/sandstone/128_patches/masks"
# files = os.listdir(path)
# files = sorted_alphanumeric(files)
# for i in tqdm(files):
#   if i == '36.png':
#     break
#   else:
#     img = cv2.imread(path + '/'+i,1)
# # open cv reads images in BGR format so we have to convert it to RGB
# img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
# #resizing image
# img = cv2.resize(img, (SIZE, SIZE))
# img = img.astype('float32') / 255.0
# high_img.append(img_to_array(img))
# high_img.append(img_to_array(img))
# high_img = np.array(high_img)

# low_img = []
# path = "/content/drive/MyDrive/Colab Notebooks/data/sandstone/128_patches/images"
# files = os.listdir(path)
# files = sorted_alphanumeric(files)
# for i in tqdm(files):
#   if i == '36.png':
#     break
#   else:
#     img = cv2.imread(path + '/'+i,1)
# img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
# #resizing image
# img = cv2.resize(img, (SIZE, SIZE))
# img = img.astype('float32') / 255.0
# low_img.append(img_to_array(img))
# low_img = np.array(low_img)

high_img = np.reshape(high_img, (len(high_img), SIZE_X, SIZE, 3))
low_img = np.reshape(low_img, (len(low_img), SIZE, SIZE, 3))
print("Shape of training images:", high_img.shape)
print("Shape of test images:", low_img.shape)

for i in range(2):
    a = np.random.randint(0, len(high_img))
    plt.figure(figsize=(10,10))
    plt.subplot(1,2,1)
    plt.title('High Resolution Imge', color = 'green', fontsize = 20)
    plt.imshow(high_img[a])
    plt.axis('off')
    plt.subplot(1,2,2)
    plt.title('low Resolution Image ', color = 'black', fontsize = 20)
    plt.imshow(low_img[a])
    plt.axis('off')

# Training data: Images 0 to 30
train_high_image = high_img[:30]
train_low_image = low_img[:30]
train_high_image = np.reshape(train_high_image, (len(train_high_image), SIZE, SIZE, 3))
train_low_image = np.reshape(train_low_image, (len(train_low_image), SIZE, SIZE, 3))

# Validation data: Images 31 to 33
validation_high_image = high_img[31:37]
validation_low_image = low_img[31:37]
validation_high_image = np.reshape(validation_high_image, (len(validation_high_image), SIZE, SIZE, 3))
validation_low_image = np.reshape(validation_low_image, (len(validation_low_image), SIZE, SIZE, 3))

# Test data: Images 34 and 35
test_high_image = high_img[37:40]
test_low_image = low_img[37:40]
test_high_image = np.reshape(test_high_image, (len(test_high_image), SIZE, SIZE, 3))
test_low_image = np.reshape(test_low_image, (len(test_low_image), SIZE, SIZE, 3))

print("Shape of training images:", train_high_image.shape)
print("Shape of test images:", test_high_image.shape)
print("Shape of validation images:", validation_high_image.shape)
print("Shape of training images:", train_low_image.shape)
print("Shape of test images:", test_low_image.shape)
print("Shape of validation images:", validation_low_image.shape)

"""# ARCITECTURE OF MODEL

"""

from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Conv2D, MaxPooling2D, UpSampling2D, concatenate, Conv2DTranspose, BatchNormalization, Dropout, Lambda
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.layers import Activation, MaxPool2D, Concatenate




def conv_block(input, num_filters):
    x = Conv2D(num_filters, 3, padding="same")(input)
    x = BatchNormalization()(x)
    x = Activation("relu")(x)
    x = Dropout(0.2)(x)  # Add dropout layer with a dropout rate
    x = Conv2D(num_filters, 3, padding="same")(x)
    x = BatchNormalization()(x)
    x = Activation("relu")(x)

    return x

#Encoder block: Conv block followed by maxpooling
def encoder_block(input, num_filters):
    x = conv_block(input, num_filters)
    p = MaxPool2D((2, 2))(x)
    return x, p

#Decoder block
#skip features gets input from encoder for concatenation

def decoder_block(input, skip_features, num_filters):
    x = Conv2DTranspose(num_filters, (2, 2), strides=2, padding="same")(input)
    x = Concatenate()([x, skip_features])
    x = conv_block(x, num_filters)
    return x

#Build Unet using the blocks
def build_unet(input_shape):
    inputs = Input(shape=(256,256,3))

    s1, p1 = encoder_block(inputs, 64)
    s2, p2 = encoder_block(p1, 128)
    s3, p3 = encoder_block(p2, 256)
    s4, p4 = encoder_block(p3, 512)

    b1 = conv_block(p4, 1024)             #Bridge

    d1 = decoder_block(b1, s4, 512)
    d2 = decoder_block(d1, s3, 256)
    d3 = decoder_block(d2, s2, 128)
    d4 = decoder_block(d3, s1, 64)


    outputs = Conv2D(3, 1, padding="same", activation="linear")(d4)  #Binary (can be multiclass)

    # outputs = Conv2D(3, 1, padding="same", activation="LeakyReLU")(d4)  #Binary (can be multiclass)
    model = Model(inputs, outputs, name="U-Net")

    model.summary()
    return model
inputs = Input(shape=(256,256,3))
model = build_unet(inputs)
plot_model(model, to_file ='super_res(U-NET).png',show_shapes=True)

def pixel_mse_loss(x,y):
    return tf.reduce_mean( (x - y) ** 2 )

model.compile(optimizer = tf.keras.optimizers.Adam(learning_rate = 0.001), loss = pixel_mse_loss, metrics = ['acc'])
model.summary()
plot_model(model, to_file ='super_res(U-NET).png',show_shapes=True)

history = model.fit(train_low_image, train_high_image, epochs = 50, batch_size = 1, validation_data = (validation_low_image,validation_high_image))

import matplotlib.pyplot as plt

# Assuming you have the history object returned by model.fit
# history = model
# Plot training and validation loss
loss = history.history['loss']
val_loss = history.history['val_loss']
epochs = range(1, len(loss) + 1)

plt.figure()
plt.plot(epochs, loss, 'y', label='Training loss')
plt.plot(epochs, val_loss, 'r', label='Validation loss')
plt.title('Training and validation loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()
plt.show()

# Plot training and validation accuracy
acc = history.history['acc']  # Use 'acc' for accuracy metric
val_acc = history.history['val_acc']

plt.figure()
plt.plot(epochs, acc, 'y', label='Training accuracy')
plt.plot(epochs, val_acc, 'r', label='Validation accuracy')
plt.title('Training and validation accuracy')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()
plt.show()

model.save('superresolution_unet.h5')

def PSNR(y_true,y_pred):
    mse=tf.reduce_mean( (y_true - y_pred) ** 2 )
    return 20 * log10(1/ (mse ** 0.5))

def log10(x):
    numerator = tf.math.log(x)
    denominator = tf.math.log(tf.constant(10, dtype=numerator.dtype))
    return numerator / denominator

def pixel_MSE(y_true,y_pred):
    return tf.reduce_mean( (y_true - y_pred) ** 2 )

def plot_images(high,low,predicted):
    plt.figure(figsize=(15,15))
    plt.subplot(1,3,1)
    plt.title('High Image', color = 'green', fontsize = 20)
    plt.imshow(high)
    plt.subplot(1,3,2)
    plt.title('Low Image ', color = 'black', fontsize = 20)
    plt.imshow(low)
    plt.subplot(1,3,3)
    plt.title('Predicted Image ', color = 'Red', fontsize = 20)
    plt.imshow(predicted)

    plt.show()

for i in range(0,1):

    predicted = np.clip(model.predict(test_low_image[i].reshape(1,SIZE, SIZE,3)),0.0,1.0).reshape(SIZE, SIZE,3)
    plot_images(test_high_image[i],test_low_image[i],predicted)
    print('PSNR',PSNR(test_high_image[i],predicted),'dB', "SSIM",tf.image.ssim(test_high_image[i],predicted,max_val=1))