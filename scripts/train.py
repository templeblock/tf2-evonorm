"""
Defines ResNet architectures and train on Cifar-10

Block/Stack decomposition is heavily inspired from official TF/Keras implementation of ResNet
"""
import numpy as np
import tensorflow as tf

from scripts.resnet import ResnetBuilder, BATCH_NORM_NAME, EVONORM_S0_NAME


INPUT_SHAPE = (224, 224, 3)


kwargs = {
    "backend": tf.keras.backend,
    "layers": tf.keras.layers,
    "utils": tf.keras.utils,
    "models": tf.keras.models,
}


if __name__ == "__main__":
    (x_train, y_train), (x_test, y_test) = tf.keras.datasets.cifar10.load_data()
    x_train = x_train.astype("float32") / 255.
    x_test = x_test.astype("float32") / 255.
    y_train = tf.keras.utils.to_categorical(y_train)
    y_test = tf.keras.utils.to_categorical(y_test)

    num_classes = 10
    batch_size = 64
    epochs = 30

    def scheduler(epoch):
        if epoch < 10:
            return 0.001
        else:
            return 0.001 * tf.math.exp(0.1 * (10 - epoch))

    lr_scheduler_callback = tf.keras.callbacks.LearningRateScheduler(scheduler)

    evonorm_model = ResnetBuilder.build_resnet_18(INPUT_SHAPE, num_classes, block_fn_name=EVONORM_S0_NAME)

    evonorm_model.compile(loss="categorical_crossentropy", optimizer="sgd", metrics=["accuracy"])

    evonorm_model.fit(
        # tf.keras.preprocessing.image.ImageDataGenerator(
        #     rescale=(224, 224, 3)
        # ).flow(x_train, y=y_train, batch_size=batch_size),
        # validation_data=tf.keras.preprocessing.image.ImageDataGenerator(
        #     rescale=(224, 224, 3)
        # ).flow(x_test, y=y_test, batch_size=batch_size),
        # epochs=epochs,
        # callbacks=[
        #     tf.keras.callbacks.TensorBoard("logs/resnet_evonorm"),
        #     lr_scheduler_callback,
        #     tf.keras.callbacks.ModelCheckpoint("models/resnet_evonorm", monitor="val_loss", save_best_only=True)
        # ],
        np.random.random((128, *INPUT_SHAPE)),
        np.zeros((128, num_classes)),
        batch_size=16

    )

    model = ResnetBuilder.build_resnet_18(INPUT_SHAPE, num_classes, block_fn_name=BATCH_NORM_NAME)

    model.compile(loss="categorical_crossentropy", optimizer="adam", metrics=["accuracy"])

    model.fit(
        tf.keras.preprocessing.image.ImageDataGenerator(
            rescale=(224, 224, 3)
        ).flow(x_train, y=y_train, batch_size=batch_size),
        validation_data=tf.keras.preprocessing.image.ImageDataGenerator(
            rescale=(224, 224, 3)
        ).flow(x_test, y=y_test, batch_size=batch_size),
        epochs=epochs,
        callbacks=[
            tf.keras.callbacks.TensorBoard("logs/resnet50"),
            lr_scheduler_callback,
            tf.keras.callbacks.ModelCheckpoint("models/resnet", monitor="val_loss", save_best_only=True)
        ]
    )

