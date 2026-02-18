import numpy as np
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Dense, Input
import os

r = 102303748
data_file = "india-air-quality-data.csv"
noise_dim = 10
epochs = 3000
batch_size = 64

a_r = 0.5 * (r % 7)
b_r = 0.3 * ((r % 5) + 1)

print("a_r =", a_r)
print("b_r =", b_r)

df = pd.read_csv(data_file, encoding="latin1")
x = pd.to_numeric(df["no2"], errors="coerce").dropna().values.astype(np.float32)

z = x + a_r * np.sin(b_r * x)

generator = Sequential([
    Dense(64, activation="relu", input_shape=(noise_dim,)),
    Dense(64, activation="relu"),
    Dense(1)
])

discriminator = Sequential([
    Dense(64, activation="relu", input_shape=(1,)),
    Dense(64, activation="relu"),
    Dense(1, activation="sigmoid")
])

discriminator.compile(
    optimizer=tf.keras.optimizers.Adam(0.0004),
    loss="binary_crossentropy"
)

discriminator.trainable = False
noise_input = Input(shape=(noise_dim,))
fake = generator(noise_input)
validity = discriminator(fake)

gan = Model(noise_input, validity)
gan.compile(
    optimizer=tf.keras.optimizers.Adam(0.0004),
    loss="binary_crossentropy"
)

real_labels = np.ones((batch_size, 1))
fake_labels = np.zeros((batch_size, 1))

for epoch in range(epochs):

    idx = np.random.randint(0, len(z), batch_size)
    real_samples = z[idx].reshape(-1, 1)

    noise = np.random.normal(0, 1, (batch_size, noise_dim))
    fake_samples = generator.predict(noise, verbose=0)

    discriminator.trainable = True
    discriminator.train_on_batch(real_samples, real_labels)
    discriminator.train_on_batch(fake_samples, fake_labels)

    noise = np.random.normal(0, 1, (batch_size, noise_dim))
    discriminator.trainable = False
    gan.train_on_batch(noise, real_labels)

    if epoch % 300 == 0:
        print("Epoch", epoch)

noise = np.random.normal(0, 1, (6000, noise_dim))
z_fake = generator.predict(noise).flatten()

print("\nStatistics")
print("Real mean:", np.mean(z))
print("Generated mean:", np.mean(z_fake))
print("Real std:", np.std(z))
print("Generated std:", np.std(z_fake))

plt.figure(figsize=(8,5))
plt.hist(z_fake, bins=70, density=True)
plt.xlabel("z")
plt.ylabel("Density")
plt.title("PDF from GAN Samples")

plt.savefig("gan_pdf.png", dpi=300)
plt.show()
