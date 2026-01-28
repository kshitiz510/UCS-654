# Data Generation using SUMO for Machine Learning

## 1. Simulator

This project uses SUMO (Simulation of Urban Mobility), a microscopic traffic simulator listed in the Wikipedia list of computer simulation software.

## 2. Simulation Scenario

A single-lane urban road of length 1 km with a speed limit of 50 km/h was modeled. Vehicle dynamics followed SUMO’s default car-following model.

## 3. Parameter Generation

Traffic demand was derived from road capacity theory. Vehicle arrivals were modeled as a Poisson process with traffic flow varying between 600 and 1800 vehicles per hour.

## 4. Data Generation

1000 traffic simulations were executed. For each simulation, average travel time was recorded from SUMO’s tripinfo output.

## 5. Machine Learning Models

Seven regression models were evaluated:

- Linear Regression
- Ridge Regression
- Lasso Regression
- Decision Tree
- Random Forest
- Gradient Boosting
- Support Vector Regression

## 6. Evaluation Metrics

Models were compared using R² Score and Mean Squared Error (MSE).

## 7. Results

Random Forest achieved the highest R² score, indicating strong performance in modeling nonlinear traffic dynamics.

## 8. Conclusion

The study demonstrates how realistic traffic simulations can be used to generate high-quality datasets for machine learning model evaluation.
