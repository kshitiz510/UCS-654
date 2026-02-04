import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score

from imblearn.over_sampling import SMOTE, RandomOverSampler
from imblearn.under_sampling import RandomUnderSampler, TomekLinks
from imblearn.combine import SMOTEENN

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC


os.makedirs("results", exist_ok=True)
sns.set(style="whitegrid")

# 1. Load Dataset
df = pd.read_csv("Creditcard_data.csv")

X = df.drop("Class", axis=1)
y = df["Class"]

print("Original Class Distribution:")
print(y.value_counts())

# 2. Balance Dataset (SMOTE)
smote = SMOTE(random_state=42)
X_bal, y_bal = smote.fit_resample(X, y)

print("\nBalanced Class Distribution:")
print(pd.Series(y_bal).value_counts())

# 3. Create Five Samples
samples = []
for seed in range(5):
    X_train, X_test, y_train, y_test = train_test_split(
        X_bal, y_bal, test_size=0.3, random_state=seed
    )
    samples.append((X_train, X_test, y_train, y_test))

# 4. Sampling Techniques
samplers = {
    "Sampling1": RandomUnderSampler(random_state=42),
    "Sampling2": RandomOverSampler(random_state=42),
    "Sampling3": SMOTE(random_state=42),
    "Sampling4": TomekLinks(),
    "Sampling5": SMOTEENN(random_state=42)
}

# 5. Models
models = {
    "M1": LogisticRegression(max_iter=3000),
    "M2": DecisionTreeClassifier(),
    "M3": RandomForestClassifier(),
    "M4": KNeighborsClassifier(),
    "M5": SVC()
}

# 6. Training & Evaluation
results = {}

for samp_name, sampler in samplers.items():
    results[samp_name] = {}

    for model_name, model in models.items():
        accuracies = []

        for X_train, X_test, y_train, y_test in samples:
            X_res, y_res = sampler.fit_resample(X_train, y_train)

            scaler = StandardScaler()
            X_res = scaler.fit_transform(X_res)
            X_test_scaled = scaler.transform(X_test)

            model.fit(X_res, y_res)
            preds = model.predict(X_test_scaled)

            accuracies.append(accuracy_score(y_test, preds))

        results[samp_name][model_name] = np.mean(accuracies)

results_df = pd.DataFrame(results).T
print("\nAccuracy Table:")
print(results_df)

# 7. Accuracy Heatmap
plt.figure(figsize=(10, 6))
sns.heatmap(
    results_df,
    annot=True,
    fmt=".3f",
    cmap="viridis",
    linewidths=0.5
)
plt.title("Accuracy Comparison: Sampling Techniques vs Models")
plt.xlabel("Models")
plt.ylabel("Sampling Techniques")
plt.tight_layout()
plt.savefig("results/accuracy_table.png", dpi=300)
plt.close()

# 8. Best Sampling Technique per Model
best_sampling = results_df.idxmax()

sampling_to_num = {
    "Sampling1": 1,
    "Sampling2": 2,
    "Sampling3": 3,
    "Sampling4": 4,
    "Sampling5": 5
}

best_sampling_numeric = best_sampling.map(sampling_to_num)

plt.figure(figsize=(8, 5))
bars = plt.bar(best_sampling_numeric.index, best_sampling_numeric.values)
plt.yticks([1,2,3,4,5], sampling_to_num.keys())
plt.xlabel("Models")
plt.ylabel("Best Sampling Technique")
plt.title("Best Sampling Technique per Model")

for bar, label in zip(bars, best_sampling.values):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.05,
        label,
        ha="center",
        fontsize=9
    )

plt.tight_layout()
plt.savefig("results/best_sampling_per_model.png", dpi=300)
plt.close()

print("\nBest Sampling Technique per Model:")
print(best_sampling)
