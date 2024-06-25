import os
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.layers import Input, GlobalAveragePooling2D, Dense
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder
from PIL import Image
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import EfficientNetB2
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

def load_image_dataset(data_dir, target_size=(224, 224)):
    dataset = []
    labels = []
    label_encoder = LabelEncoder()
    for label in os.listdir(data_dir):
        label_dir = os.path.join(data_dir, label)
        if not os.path.isdir(label_dir):
            continue
        for img_name in os.listdir(label_dir):
            img_path = os.path.join(label_dir, img_name)
            if not img_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                continue
            img = Image.open(img_path).convert('RGB')
            img_resized = img.resize(target_size)
            dataset.append(np.array(img_resized))
            labels.append(label)
    encoded_labels = label_encoder.fit_transform(labels)
    return np.array(dataset), encoded_labels, label_encoder.classes_

# Load and preprocess data
data_dir = 'assets/images/'
images, labels, class_names = load_image_dataset(data_dir)
X_train, X_test, y_train, y_test = train_test_split(images, labels, test_size=0.1, random_state=42)

# Data Augmentation
train_datagen = ImageDataGenerator(
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    preprocessing_function=tf.keras.applications.efficientnet.preprocess_input
)
train_generator = train_datagen.flow(X_train, y_train, batch_size=32)

# Load pre-trained EfficientNetB2 model
base_model = EfficientNetB2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))

# Add classification head
x = GlobalAveragePooling2D()(base_model.output)
x = Dense(256, activation='relu')(x)
outputs = Dense(len(class_names), activation='softmax')(x)
model = Model(inputs=base_model.input, outputs=outputs)

# Fine-tune the model
for layer in base_model.layers:
    layer.trainable = False

# Create the optimizer with specified learning rate
optimizer = Adam(learning_rate=0.001)

# Compile the model with the optimizer
model.compile(optimizer=optimizer, loss='sparse_categorical_crossentropy', metrics=['accuracy'])


# Early stopping and learning rate reduction callbacks
early_stopping = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)
reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=2, min_lr=1e-6)

# Train the model
history = model.fit(train_generator, epochs=20, validation_data=(X_test, y_test), callbacks=[early_stopping, reduce_lr])

# Evaluate the model
loss, accuracy = model.evaluate(X_test, y_test)
print("Test Loss:", loss)
print("Test Accuracy:", accuracy)

# Save the model
model.save('food_classification_model.keras')