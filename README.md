# Composite Behavioral Modeling for Identity Theft Detection

## Project Overview
This project is a Django-based web application designed to detect identity theft and fraud through **Composite Behavioral Modeling**. It leverages multiple machine learning algorithms to analyze transaction patterns and identify suspicious activities.

## Key Features

### 👤 Remote User
*   **Registration & Login**: Secure user portal for registration and authentication.
*   **Profile Management**: View and manage personal details.
*   **Theft Status Prediction**: Input transaction details (Account ID, Transaction ID, Income, Credit, etc.) to get an instant prediction on potential fraud.
*   **Behavioral Analysis**: Uses composite modeling to analyze user-specific behavioral data.

### 🏢 Service Provider (Admin)
*   **User Management**: View all registered users and their profiles.
*   **Prediction Monitoring**: Oversee all theft status predictions made by the system.
*   **Machine Learning Dashboard**:
    *   **Train Models**: Manually trigger model training on the provided dataset.
    *   **Accuracy Comparison**: View performance metrics (Accuracy, Classification Report, Confusion Matrix) for various algorithms:
        *   Naive Bayes
        *   SVM (Support Vector Machine)
        *   Logistic Regression
        *   Decision Tree / Extra Tree Classifier
        *   Gradient Boosting
    *   **Visual Analytics**: View interactive charts for detection ratios and algorithm accuracies.
*   **Data Export**: Download predicted transaction datasets in `.xls` format.

## Technology Stack
*   **Backend**: Python (Django Framework)
*   **Frontend**: HTML5, CSS3 (Brutalist style)
*   **Database**: SQLite (Migrated from MySQL for ease of local setup)
*   **Machine Learning**: Scikit-learn, Pandas, NumPy
*   **Export Tools**: xlwt (Excel generation)

## Installation & Setup

### Prerequisites
*   Python 3.12 or higher
*   `pip` (Python package manager)

### Local Setup
1.  **Clone the Project**:
    ```bash
    git clone <repository-url>
    cd Composite_Behavioral_Modeling
    ```

2.  **Create Virtual Environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Database Migration**:
    ```bash
    python manage.py migrate
    ```

5.  **Run the Server**:
    ```bash
    python manage.py runserver
    ```

6.  **Access the Application**:
    Open `http://127.0.0.1:8000` in your browser.

## Database Configuration
The project is currently configured to use **SQLite** for a "zero-setup" experience. If you wish to use **MySQL**, revert the changes in `settings.py` and ensure the `pymysql` initialization in `__init__.py` is uncommented.

## Default Admin Credentials
*   **Username**: `Admin`
*   **Password**: `Admin`

---
*Created as part of the Composite Behavioral Modeling research project.*
