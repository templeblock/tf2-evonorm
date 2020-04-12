import tensorflow as tf
from keras_applications import resnet_common

from evonorm.evonorm import EvoNormS0


INPUT_SHAPE = (224, 224, 3)


kwargs = {
    "backend": tf.keras.backend,
    "layers": tf.keras.layers,
    "utils": tf.keras.utils,
    "models": tf.keras.models,
}

resnet50_original = resnet_common.ResNet50(input_shape=INPUT_SHAPE, weights="imagenet", **kwargs)
resnet50_original.summary()


def evonorm_block_fn(x, filters, kernel_size=3, stride=1,
           conv_shortcut=True, name=None):
    """A residual block.

    # Arguments
        x: input tensor.
        filters: integer, filters of the bottleneck layer.
        kernel_size: default 3, kernel size of the bottleneck layer.
        stride: default 1, stride of the first layer.
        conv_shortcut: default True, use convolution shortcut if True,
            otherwise identity shortcut.
        name: string, block label.

    # Returns
        Output tensor for the residual block.
    """
    if conv_shortcut is True:
        shortcut = tf.keras.layers.Conv2D(4 * filters, 1, strides=stride,
                                 name=name + '_0_conv')(x)
        shortcut = EvoNormS0(channels=4 * filters)(shortcut)
    else:
        shortcut = x

    x = tf.keras.layers.Conv2D(filters, 1, strides=stride, name=name + '_1_conv')(x)
    x = EvoNormS0(channels=filters)(x)
    x = tf.keras.layers.Conv2D(filters, kernel_size, padding='SAME',
                      name=name + '_2_conv')(x)
    x = EvoNormS0(channels=filters)(x)
    x = tf.keras.layers.Conv2D(4 * filters, 1, name=name + '_3_conv')(x)

    x = EvoNormS0(channels=4 * filters)(x)
    x = tf.keras.layers.Add(name=name + '_add')([shortcut, x])
    x = tf.keras.layers.Activation('relu', name=name + '_out')(x)
    return x

def stack_evonorm(x, filters, blocks, stride1=2, name=None):
    """A set of stacked residual blocks.

    # Arguments
        x: input tensor.
        filters: integer, filters of the bottleneck layer in a block.
        blocks: integer, blocks in the stacked blocks.
        stride1: default 2, stride of the first layer in the first block.
        name: string, stack label.

    # Returns
        Output tensor for the stacked blocks.
    """
    x = evonorm_block_fn(x, filters, stride=stride1, name=name + '_block1')
    for i in range(2, blocks + 1):
        x = evonorm_block_fn(x, filters, conv_shortcut=False, name=name + '_block' + str(i))
    return x


def evonorm_stack_fn(x):
    x = stack_evonorm(x, 64, 3, stride1=1, name='conv2')
    x = stack_evonorm(x, 128, 4, name='conv3')
    x = stack_evonorm(x, 256, 6, name='conv4')
    x = stack_evonorm(x, 512, 3, name='conv5')
    return x


model = resnet_common.ResNet(evonorm_stack_fn, False, True, 'resnet50',
                  include_top=True, weights=None,
                  input_tensor=None, input_shape=INPUT_SHAPE,
                  pooling=None, classes=1000,
                  **kwargs)
model.summary()