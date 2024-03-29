# -*- coding: utf-8 -*-
"""Unet from scratch.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/15rmfqS8tVtBaqNH5c_rmV3N1RI-0raYX
"""

import tensorflow as tf
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Conv2DTranspose, Input, concatenate
from tensorflow.keras.models import Model

#Let's create a function for one step of the encoder block, so as to increase the reusability when making custom unets

def encoder_block(filters, inputs):
  x = Conv2D(filters, kernel_size = (3,3), padding = 'same', strides = 1, activation = 'relu')(inputs)
  s = Conv2D(filters, kernel_size = (3,3), padding = 'same', strides = 1, activation = 'relu')(x)
  p = MaxPooling2D(pool_size = (2,2), padding = 'same')(s)
  return s, p #p provides the input to the next encoder block and s provides the context to the symmetrically opposte decoder block

#Baseline layer is just a binch on Convolutional Layers to extract high level features from the downsampled Image
#As the number of baselines to include is highly related to the task, we don't necessarily need a function for it
def baseline_layer(filters, inputs):
  x = Conv2D(filters, kernel_size = (3,3), padding = 'same', strides = 1, activation = 'relu')(inputs)
  x = Conv2D(filters, kernel_size = (3,3), padding = 'same', strides = 1, activation = 'relu')(x)
  return x

#Decoder Block

def decoder_block(filters, connections, inputs):
  x = Conv2DTranspose(filters, kernel_size = (2,2), padding = 'same', activation = 'relu', strides = 2)(inputs)
  skip_connections = concatenate([x, connections], axis = -1)
  x = Conv2D(filters, kernel_size = (2,2), padding = 'same', activation = 'relu')(skip_connections)
  x = Conv2D(filters, kernel_size = (2,2), padding = 'same', activation = 'relu')(x)
  return x

def unet():
  #Defining the input layer and specifying the shape of the images
  inputs = Input(shape = (256,256,1))

  #defining the encoder
  s1, p1 = encoder_block(64, inputs = inputs)
  s2, p2 = encoder_block(128, inputs = p1)
  s3, p3 = encoder_block(256, inputs = p2)
  s4, p4 = encoder_block(512, inputs = p3)

  #Setting up the baseline
  baseline = baseline_layer(1024, p4)

  #Defining the entire decoder
  d1 = decoder_block(512, s4, baseline)
  d2 = decoder_block(256, s3, d1)
  d3 = decoder_block(128, s2, d2)
  d4 = decoder_block(64, s1, d3)

  #Setting up the output function for binary classification of pixels
  outputs = Conv2D(1, 1, activation = 'sigmoid')(d4)

  #Finalizing the model
  model = Model(inputs = inputs, outputs = outputs, name = 'Unet')

  return model