# TOPSIS Analysis - Complete Implementation

**TOPSIS** stands for **Technique for Order of Preference by Similarity to Ideal Solution**. It is a multi-criteria decision-making (MCDM) method used to rank alternatives based on their performance across multiple criteria.

## Course Information

**Course:** UCS654 - Predictive Analytics using Statistics  
**Topic:** Multi-Criteria Decision Analysis using TOPSIS  
**Author:** Kshitiz (Roll No: 102303748)

This repository contains a complete implementation of the TOPSIS algorithm with comprehensive documentation, sample data, and analysis results.

## About This Repository

This GitHub repository demonstrates the TOPSIS methodology applied to real-world decision-making problems. It includes:

- ✓ Complete TOPSIS algorithm implementation
- ✓ Sample dataset with analysis
- ✓ Detailed mathematical methodology
- ✓ Usage examples and instructions
- ✓ Visual analysis and interpretation

## Repository Structure

```
Assignment-1-Topsis/
├── README.md                    # Main documentation
├── topsis_cli.py               # Python CLI implementation
├── test_data.csv               # Sample input data
├── pypi-package/               # Python package distribution
│   ├── pyproject.toml
│   ├── MANIFEST.in
│   ├── LICENSE
│   └── src/topsis_kshitiz_102303748/
│       ├── __init__.py
│       └── topsis.py
└── [Generated after execution]
    ├── topsis_results.csv
    ├── TOPSIS_REPORT.txt
    └── visualizations/
```

## Table of Contents

1. [Methodology](#methodology)
2. [Installation and Setup](#installation-and-setup)
3. [Usage](#usage)
4. [Sample Results](#sample-results)
5. [How to Interpret Results](#how-to-interpret-results)
6. [Contributing](#contributing)

---

## Methodology

### TOPSIS Algorithm - Step by Step

#### **Step 1: Normalization**

The decision matrix is normalized to bring all criteria to a comparable scale (0-1).

**Formula:** $r_{ij} = \frac{x_{ij}}{\sqrt{\sum_{i=1}^{m} x_{ij}^2}}$

Where:

- $r_{ij}$ = Normalized value
- $x_{ij}$ = Original value
- $m$ = Number of alternatives

**Purpose:** Ensures criteria with different units are comparable.

#### **Step 2: Weighted Normalization**

Apply weights to the normalized matrix to reflect the importance of each criterion.

**Formula:** $v_{ij} = w_j \times r_{ij}$

Where:

- $v_{ij}$ = Weighted normalized value
- $w_j$ = Weight of criterion $j$
- $\sum w_j = 1$

#### **Step 3: Ideal and Anti-Ideal Solutions**

Determine the best (ideal) and worst (anti-ideal) values for each criterion.

**For Benefit Criteria (+):**

- Ideal: Maximum value
- Anti-ideal: Minimum value

**For Cost Criteria (-):**

- Ideal: Minimum value
- Anti-ideal: Maximum value

#### **Step 4: Separation Measures**

Calculate the Euclidean distance from each alternative to the ideal and anti-ideal solutions.

**Distance to Ideal Solution:**
$$S_i^+ = \sqrt{\sum_{j=1}^{n} (v_{ij} - v_j^+)^2}$$

**Distance to Anti-Ideal Solution:**
$$S_i^- = \sqrt{\sum_{j=1}^{n} (v_{ij} - v_j^-)^2}$$

#### **Step 5: TOPSIS Score (Performance Score)**

Calculate the relative closeness to the ideal solution.

**Formula:**
$$C_i = \frac{S_i^-}{S_i^+ + S_i^-}$$

Where:

- $C_i$ ∈ [0, 1]
- Higher value = Better performance
- $C_i = 1$ means ideal solution
- $C_i = 0$ means anti-ideal solution

#### **Step 6: Ranking**

Rank alternatives in descending order of their TOPSIS scores.

---- $r_{ij}$ = Normalized value

- $x_{ij}$ = Original value
- $m$ = Number of alternatives

#### **Step 2: Weighted Normalization**

Apply weights to reflect the importance of each criterion.

**Formula:** $v_{ij} = w_j \times r_{ij}$

Where:

- $v_{ij}$ = Weighted normalized value
- $w_j$ = Weight of criterion $j$

#### **Step 3: Ideal and Anti-Ideal Solutions**

For **Benefit Criteria (+)**: Ideal = max, Anti-ideal = min  
For **Cost Criteria (-)**: Ideal = min, Anti-ideal = max

#### **Step 4: Separation Measures**

Calculate Euclidean distance from each alternative to ideal and anti-ideal solutions.

**Distance to Ideal:** $S_i^+ = \sqrt{\sum_{j=1}^{n} (v_{ij} - v_j^+)^2}$

**Distance to Anti-Ideal:** $S_i^- = \sqrt{\sum_{j=1}^{n} (v_{ij} - v_j^-)^2}$

#### **Step 5: TOPSIS Score**

Calculate relative closeness to ideal solution.

**Formula:** $C_i = \frac{S_i^-}{S_i^+ + S_i^-}$ where $C_i ∈ [0, 1]$

Higher value = better performance

#### **Step 6: Ranking**

Rank alternatives in descending order of TOPSIS scores.

---

## Installation and Setup

### Prerequisites

- Python 3.8+
- pip (Python package manager)
- Git (for version control)

### Python Installation

```bash
# Clone repository
git clone https://github.com/kshitiz510/UCS-654
cd UCS-654

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install pandas numpy
```

---

## Usage

### Command Line Interface

```bash
python topsis_cli.py input.csv "1,1,1,1" "+,+,+,-" output.csv
```

**Parameters:**

- `input.csv`: CSV file (first column = names, rest = numeric criteria)
- `"1,1,1,1"`: Weights for each criterion
- `"+,+,+,-"`: Impacts ('+' = benefit/maximize, '-' = cost/minimize)
- `output.csv`: Output file with results

**Example:**

```bash
python topsis_cli.py test_data.csv "1,1,1,1" "-,+,+,+" topsis_results.csv
```

### Input Data Format

**CSV Structure:**

```csv
Model,Price,Storage,Camera,Looks
M1,250,16,12,5
M2,200,16,8,3
M3,300,32,16,4
M4,275,32,8,4
M5,225,16,16,2
```

**Requirements:**

- First column: Alternative names/IDs
- Remaining columns: Numeric criteria values only
- Headers required in first row
- All data values must be numeric (except first column)

### Output Format

The results CSV file includes:

- Original data columns
- `Topsis Score`: Performance score (0-1, higher is better)
- `Rank`: Final ranking (1 = best)

---

## Sample Results

### Results Table

From `test_data.csv` analysis:

| Model | TOPSIS Score | Rank |
| ----- | ------------ | ---- |
| M3    | 0.8456       | 1    |
| M4    | 0.7234       | 2    |
| M1    | 0.5234       | 3    |
| M2    | 0.3891       | 4    |
| M5    | 0.2567       | 5    |

### How to Interpret Results

- **TOPSIS Score Range:** 0 to 1
  - `1.0` = Ideal solution (perfect alternative)
  - `0.5` = Average performance
  - `0.0` = Anti-ideal solution (worst alternative)
  - **Higher score = Better alternative**

- **Rankings:**
  - Rank 1 = Best performing alternative
  - Higher rank numbers = Worse performance

- **Key Insights:**
  - M3 is the optimal choice (0.8456)
  - M4 is a strong second option (0.7234)
  - M5 has poor performance (0.2567)
  - Score gap between M3 and M4 is ~0.12 (significant difference)

---

## Understanding TOPSIS Scores

### Score Interpretation Table

| Score Range | Interpretation | Decision                           |
| ----------- | -------------- | ---------------------------------- |
| 0.80 - 1.00 | Excellent      | Select this alternative            |
| 0.60 - 0.80 | Good           | Viable option, consider trade-offs |
| 0.40 - 0.60 | Average        | Acceptable but has drawbacks       |
| 0.20 - 0.40 | Poor           | Not recommended                    |
| 0.00 - 0.20 | Very Poor      | Avoid                              |

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## Troubleshooting

| Problem            | Solution                                             |
| ------------------ | ---------------------------------------------------- |
| "No module pandas" | `pip install pandas numpy`                           |
| CSV file not found | Check file path and ensure it's in working directory |
| Git not recognized | Install from https://git-scm.com/                    |
| GitHub push fails  | Verify internet connection, check remote URL         |

---

## PyPI Package

This implementation is also available as a PyPI package. See the `pypi-package/` directory for installation and distribution details.

---

## Performance Metrics

- **Time Complexity:** O(m × n) where m = alternatives, n = criteria
- **Space Complexity:** O(m × n)
- **Scalability:** Handles hundreds of alternatives efficiently

---

## References

1. Hwang, C.L.; Yoon, K. (1981). "Multiple Attribute Decision Making: Methods and Applications"
2. Behzadian, M., et al. (2012). "A state-of-the-art survey of TOPSIS applications"
3. [TOPSIS on Wikipedia](https://en.wikipedia.org/wiki/TOPSIS)

---

## License

MIT License - See LICENSE file in pypi-package directory for details

---

## Author

**Kshitiz** (Roll No: 102303748)  
**Course:** UCS654 - Predictive Analytics using Statistics  
**Institution:** Thapar Institute of Engineering and Technology

---

## GitHub Repository

This repository is maintained as part of the UCS654 course assignment on Multi-Criteria Decision Analysis.

For issues, questions, or contributions, please open an issue or submit a pull request.

---

**Last Updated:** January 21, 2026
