# Get Center point from ML way
# 2018-01-12

import tensorflow as tf
import cv2
import pickle
import numpy as np


def weight_variable(shape):
    initial = tf.truncated_normal(shape=shape, stddev=0.1)
    return tf.Variable(initial)


def bias_variable(shape):
    initial = tf.constant(0.1, shape=shape)
    return tf.Variable(initial)


def conv2d(x, W):
    return tf.nn.conv2d(x, W, strides=[1, 2, 2, 1], padding='SAME')


def max_pool_2x2(x):
    return tf.nn.max_pool(x, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')


def createNetwork():
    # 80*80 -> 32*32 -> 32*32 -> 1*1
    x_image = tf.placeholder("float", [None, 240, 240, 1])

    # Layer 1
    W_conv1 = weight_variable([5, 5, 1, 32])
    b_conv1 = bias_variable([32])
    h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)
    h_pool1 = max_pool_2x2(h_conv1)

    # Dense Layer
    W_d = weight_variable([60 * 60 * 32, 512])
    b_d = bias_variable([512])
    h_pool1_flat = tf.reshape(h_pool1, [-1, 60 * 60 * 32])
    h_out = tf.nn.relu(tf.matmul(h_pool1_flat, W_d) + b_d)

    # Dropout Layer
    keep_prob = tf.placeholder(tf.float32)
    h_drop = tf.nn.dropout(h_out, keep_prob=keep_prob)

    # Readout
    W_out = weight_variable([512, 1])
    b_out = bias_variable([1])
    y_out = tf.matmul(h_drop, W_out) + b_out

    return x_image, keep_prob, y_out


def trainNetwork(x_image, y_out, keep_prob, sess):
    # loss
    y_ = tf.placeholder(tf.float32)
    loss = tf.reduce_mean(tf.square(y_out - y_))
    train_step = tf.train.AdamOptimizer(0.001).minimize(loss)

    sess.run(tf.global_variables_initializer())
    # start Training
    t = 0
    tdata = pickle.load(open('data.ml', 'rb'))
    ximgs = []

    ximg = np.reshape(tdata[t][0], (240, 240, 1))
    ximgs.append(ximg)
    ylabel = [x[1] for x in tdata]

    train_step.run(feed_dict={y_: ylabel, x_image: ximgs, keep_prob: 0.5})
    print('Train Finished')

    cost = loss.eval(feed_dict={
        y_: ylabel, x_image: ximgs, keep_prob: 1.0})
    print('training error %g' % cost)


def learn():
    sess = tf.InteractiveSession()
    x_img, keep_prob, y_out = createNetwork()
    trainNetwork(x_img, y_out, keep_prob, sess)


learn()
