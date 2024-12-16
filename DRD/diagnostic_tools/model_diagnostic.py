import os
import numpy as np
import tensorflow as tf
import keras
import cv2
from matplotlib import cm
from PIL import Image

# Ruta al modelo
MODEL_PATH = os.path.join(os.path.dirname(
    __file__), 'InceptionV3_Full_Balanced_Strat_20Epocs.keras')

IMAGE_PATH = os.path.join(os.path.dirname(__file__), 'test_image3.jpg')

# Tamaño de las imágenes
IMG_WIDTH, IMG_HEIGHT = 512, 512


# Generar Grad-CAM con relación de aspecto original
def generate_gradcam(image_path, output_path, last_conv_layer_name=None):
    try:
        model = keras.models.load_model(MODEL_PATH)

        original_img = cv2.imread(image_path)
        original_height, original_width = original_img.shape[:2]

        img = keras.utils.load_img(
            image_path, target_size=(IMG_WIDTH, IMG_HEIGHT))
        img_array = keras.utils.img_to_array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        if not last_conv_layer_name:
            for layer in reversed(model.layers):
                if isinstance(layer, keras.layers.Conv2D):
                    last_conv_layer_name = layer.name
                    break
            if not last_conv_layer_name:
                raise ValueError(
                    "El modelo no contiene capas convolucionales.")

        grad_model = keras.models.Model(
            inputs=model.input,
            outputs=[model.get_layer(
                last_conv_layer_name).output, model.output]
        )

        with tf.GradientTape() as tape:
            conv_outputs, predictions = grad_model(img_array)
            predicted_class = tf.argmax(predictions[0])
            loss = predictions[:, predicted_class]

        grads = tape.gradient(loss, conv_outputs)
        guided_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
        conv_outputs = conv_outputs[0]

        cam = tf.reduce_sum(tf.multiply(
            guided_grads, conv_outputs), axis=-1).numpy()
        cam = np.maximum(cam, 0)
        cam = cam / cam.max()

        cam_resized = cv2.resize(cam, (original_width, original_height))
        heatmap = np.uint8(255 * cam_resized)
        heatmap = cm.jet(heatmap)[:, :, :3]
        heatmap = cv2.cvtColor(
            (heatmap * 255).astype(np.uint8), cv2.COLOR_RGB2BGR)

        superimposed_img = cv2.addWeighted(original_img, 0.6, heatmap, 0.4, 0)

        cv2.imwrite(output_path, superimposed_img)
        print(f"Grad-CAM generado y almacenado en {output_path}")
    except Exception as e:
        print(f"Error al generar Grad-CAM: {e}")
        raise


def make_prediction(image_path):
    try:
        model = keras.models.load_model(MODEL_PATH)

        image = Image.open(image_path)
        image = image.resize((IMG_WIDTH, IMG_HEIGHT))
        img_array = keras.utils.img_to_array(image)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = img_array / 255.0

        prediction = model.predict(img_array)
        predicted_class = np.argmax(prediction)

        return predicted_class
    except Exception as e:
        print(f"Error al procesar la imagen: {e}")
        raise
