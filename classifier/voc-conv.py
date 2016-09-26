from __future__ import print_function

'''

Original code:

https://github.com/aymericdamien/TensorFlow-Examples/blob/master/examples/3_NeuralNetworks/convolutional_network.py

See also

http://stackoverflow.com/questions/34340489/tensorflow-read-images-with-labels
http://stackoverflow.com/questions/37091899/how-to-actually-read-csv-data-in-tensorflow
https://gist.github.com/eerwitt/518b0c9564e500b4b50f
http://stackoverflow.com/questions/37504470/tensorflow-crashes-when-using-sess-run
http://learningtensorflow.com
http://openmachin.es/blog/tensorflow-mnist
https://freedomofkeima.com/blog/posts/flag-8-first-trial-to-image-processing-with-tensorflow

something interesting about TF

https://bamos.github.io/2016/08/09/deep-completion/

http://christopher5106.github.io/deep/learning/2015/11/11/tensorflow-google-deeplearning-library.html
https://github.com/TensorVision/TensorVision
https://indico.io/blog/tensorflow-data-inputs-part1-placeholders-protobufs-queues/

https://ischlag.github.io/2016/06/03/simple-neural-network-in-tensorflow/

here is the best explanation of how tf works:
https://ischlag.github.io/2016/06/19/tensorflow-input-pipeline-example/

how to visualize weights:

http://stackoverflow.com/questions/33783672/how-can-i-visualize-the-weightsvariables-in-cnn-in-tensorflow
https://www.snip2code.com/Snippet/1104315/Tensorflow---visualize-convolutional-fea

softmax_cross_entropy_with_logits and sparce_softmax_cross_entropy_with_logits diference:
http://stackoverflow.com/questions/37312421/tensorflow-whats-the-difference-between-sparse-softmax-cross-entropy-with-logi

'''

import numpy
import tensorflow as tf
import tf_visualization

# Parameters
learning_rate = 0.001

image_width = 100
image_height = 100

# Network Parameters
n_input = image_width * image_height 
n_classes = 2 # MNIST total classes (0-9 digits)
dropout = 0.75 # Dropout, probability to keep units


train_amount = 90000

epochs = 1

batch_size = 200
eval_batch_size = 200

# tf Graph input
#x = tf.placeholder(tf.float32, [None, n_input])
#y = tf.placeholder(tf.float32, [None, n_classes])

keep_prob = tf.placeholder(tf.float32) #dropout (keep probability)

# Create some wrappers for simplicity
def conv2d(x, W, b, strides = 1):
    # Conv2D wrapper, with bias and relu activation
    x = tf.nn.conv2d(x, W, strides = [1, strides, strides, 1], padding = 'SAME')
    x = tf.nn.bias_add(x, b)
    return tf.nn.relu(x)


def maxpool2d(x, k=2):
    # MaxPool2D wrapper
    return tf.nn.max_pool(x, ksize=[1, k, k, 1], strides=[1, k, k, 1],
                          padding='SAME')


# Create model
def conv_net(x, weights, biases, dropout):
    # Reshape input picture
    x = tf.reshape(x, shape = [-1, image_width, image_height, 1])

    # Convolution Layer
    conv1 = conv2d(x, weights['wc1'], biases['bc1'])
    # Max Pooling (down-sampling)
    conv1 = maxpool2d(conv1, k = 2)

    # Convolution Layer
    conv2 = conv2d(conv1, weights['wc2'], biases['bc2'])
    # Max Pooling (down-sampling)
    conv2 = maxpool2d(conv2, k = 2)

    # Fully connected layer
    # Reshape conv2 output to fit fully connected layer input
    fc1 = tf.reshape(conv2, [-1, weights['wd1'].get_shape().as_list()[0]])
    fc1 = tf.add(tf.matmul(fc1, weights['wd1']), biases['bd1'])
    fc1 = tf.nn.relu(fc1)
    # Apply Dropout
    fc1 = tf.nn.dropout(fc1, dropout)

    # Output, class prediction
    out = tf.add(tf.matmul(fc1, weights['out']), biases['out'])
    return out

# Store layers weight & bias
weights = {
    # 5x5 conv, 1 input, 32 outputs
    'wc1': tf.Variable(tf.random_normal([5, 5, 1, 32])),
    #'wc1': tf.Variable(tf.random_normal([12, 12, 1, 32])),
    #'wc1': tf.Variable(tf.zeros([5, 5, 1, 32])),
    # 5x5 conv, 32 inputs, 64 outputs
    'wc2': tf.Variable(tf.random_normal([5, 5, 32, 64])),
    #'wc2': tf.Variable(tf.random_normal([12, 12, 32, 64])),
    # fully connected, 7*7*64 inputs, 1024 outputs
    #'wd1': tf.Variable(tf.random_normal([7*7*64, 1024])),
    'wd1': tf.Variable(tf.random_normal([int((image_width / 4) * (image_height / 4) * 64), 1024])),
    # 1024 inputs, n_classes outputs (class prediction)
    'out': tf.Variable(tf.random_normal([1024, n_classes]))
}

biases = {
    'bc1': tf.Variable(tf.random_normal([32])),
    'bc2': tf.Variable(tf.random_normal([64])),
    'bd1': tf.Variable(tf.random_normal([1024])),
    'out': tf.Variable(tf.random_normal([n_classes]))
}
    
def input_data(start_index, amount, shuffle):
    
    data_folder = '/media/sf_vb-shared/data/'
        
    folder_map = tf.constant(['a', 'b'])
    label_map = tf.constant([ [0.0, 1.0], [1.0, 0.0] ])
    
    range_queue = tf.train.range_input_producer(amount, shuffle = shuffle)

    range_value = range_queue.dequeue()

#    if shuffle == False:
#    if shuffle == True:
#       range_value = tf.Print(range_value, [range_value], message = "rv: ")            

        
    per_class = int(amount / n_classes)
    class_index = tf.div(range_value, tf.constant(per_class))
               
    label = tf.gather(label_map, class_index)
    folder = tf.gather(folder_map, class_index)
    
    relative_index = tf.mod(range_value, tf.constant(per_class))
        
    abs_index = tf.add(relative_index, tf.constant(start_index))
    
    abs_index_str = tf.as_string(abs_index, width = 9, fill = '0')
    
    file_name = tf.string_join([tf.constant(data_folder), folder, tf.constant('/data'), abs_index_str, tf.constant('.png')])
    
    #file_name = tf.Print(file_name, [file_name], message = "This is file name: ")
        
    raw_data = tf.read_file(file_name)    
    
    data = tf.image.decode_png(raw_data)

    #data_shape = tf.shape(data);
    #data = tf.Print(data, [data_shape], message = "Data shape: ")            
    #data = tf.image.rgb_to_grayscale(data)
    #data = tf.image.resize_images(data, image_height, image_width)
    
    
    data = tf.reshape(data, [-1])    
    data = tf.to_float(data)
    
    return data, label
            
x, y = input_data(0, train_amount, shuffle = True)

x.set_shape([image_height * image_width])
y.set_shape([n_classes])

x_batch, y_batch = tf.train.batch([x, y], batch_size = batch_size)

# Construct model
pred = conv_net(x_batch, weights, biases, keep_prob)

# Define loss and optimizer
cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(pred, y_batch))
optimizer = tf.train.AdamOptimizer(learning_rate = learning_rate).minimize(cost)

# Define evaluation pipeline

x1, y1 = input_data(int(train_amount / n_classes), eval_batch_size, shuffle = False)
x1.set_shape([image_height * image_width])
y1.set_shape([n_classes])

x1_batch, y1_batch = tf.train.batch([x1, y1], batch_size = eval_batch_size)
pred1 = conv_net(x1_batch, weights, biases, keep_prob)
correct_pred = tf.equal(tf.argmax(pred1, 1), tf.argmax(y1_batch, 1))
accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32))

def test_accuracy():
    acc = sess.run(accuracy, feed_dict = {keep_prob: 1.0} )    
    print("Testing Accuracy:", acc )    


grid = tf_visualization.put_kernels_on_color_grid (weights['wc1'], grid_Y = 4, grid_X = 8)
#grid = tf_visualization.put_averaged_kernels_on_grid (weights['wc2'], grid_Y = 8, grid_X = 8)
#grid = tf_visualization.put_fully_connected_on_grid (weights['wd1'], grid_Y = 25, grid_X = 25)

# the end of graph construction

sess = tf.Session()

train_writer = tf.train.SummaryWriter('./train',  sess.graph)

# Initializing the variables
init = tf.initialize_all_variables()
    
sess.run(init)

coord = tf.train.Coordinator()

threads = tf.train.start_queue_runners(sess = sess, coord = coord)

# todo : print out 'batch loss'

iterations = max(1, int(train_amount / batch_size)) * epochs

for i in range(iterations):

    wc1_summary = tf.image_summary('conv1/features'+ str(i), grid, max_images = 1)

    _, summary = sess.run([optimizer, wc1_summary], feed_dict = {keep_prob: dropout} )
    #_ = sess.run([optimizer], feed_dict = {keep_prob: dropout} )
    print((i * 100) / iterations, "% done" )    
    if i % 10 == 0:
        test_accuracy()
        
    train_writer.add_summary(summary)
    
    '''
    array = sess.run(weights['wc1'])
    fname = 'conv' + str(i).zfill(9) + '.csv'
    numpy.savetxt(fname, array.flatten(), "%10.10f")
    '''
    
    '''
    array = sess.run(weights['out'])
    fname = 'out' + str(i).zfill(9) + '.csv'
    numpy.savetxt(fname, array.flatten(), "%10.10f")
    '''

                    
test_accuracy()
    
coord.request_stop()
coord.join()

sess.close()