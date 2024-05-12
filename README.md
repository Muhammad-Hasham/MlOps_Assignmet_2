# MlOps Assignmet 2

## Introduction
This documentation provides an overview of the data preprocessing steps and the setup of Data Version Control (DVC) in the context of an automated data extraction, transformation, and storage workflow using Apache Airflow.

## Workflow Overview
1. **Data Extraction:** The workflow begins with extracting data from specified sources using web scraping techniques. The extracted data includes article titles, descriptions, and their respective sources.
2. **Data Transformation:** Next, the extracted data is transformed into a structured format, typically a Pandas DataFrame, to prepare it for further processing and analysis.
3. **Data Storage and Versioning:** The transformed data is stored both locally and on Google Drive. Additionally, version control is applied using DVC to track changes and ensure reproducibility.
4. **DVC Operations:** The workflow includes tasks for adding data to DVC, committing and pushing changes to the DVC repository, and pushing data to a remote DVC storage.

## Data Preprocessing Steps
### 1. Data Extraction
- Utilizes web scraping techniques to extract data from specified sources (e.g., 'https://www.dawn.com/', 'https://www.bbc.com/') using the `requests` library and `BeautifulSoup` for HTML parsing.
- Extracted data includes article titles, descriptions, and their corresponding sources.
- Exception handling is implemented to manage HTTP errors and other potential issues during data extraction.

### 2. Data Transformation
- Transforms the extracted data into a structured format (e.g., Pandas DataFrame) using the `transform` function.
- Uses Airflow's XCom feature to pass data between tasks, ensuring seamless data flow within the workflow.
- Exception handling is implemented to manage errors that may occur during data transformation.

### 3. Data Storage and Versioning
- Stores the transformed data locally as a CSV file (`processed_data.csv`) in the specified `data_path`.
- Downloads the CSV file to Google Drive for backup and sharing purposes.
- Implements version control using DVC to track changes, create checkpoints, and commit data versions.

## DVC Setup
### 1. DVC Installation and Initialization
- DVC is installed and initialized in the project directory (`D:/Hasham/D Drive Desktop/Mlops_A2/`) to enable version control and data tracking.

### 2. DVC Operations in Workflow
- **DVC Add Operation (`dvc_add`):** Adds the `processed_data.csv` file to DVC for version tracking.
- **DVC Commit and Push Operations (`git_commit_push` and `dvc_push`):** Commits changes to the DVC repository and pushes data to a remote DVC storage for backup and collaboration.

## Challenges Encountered
- **Apache Airflow Setup:** Difficulty in setting up Apache Airflow on Windows OS due to compatibility issues and dependencies. This led to the decision of using a VirtualBox with Kali Linux to run Airflow, ensuring a more stable and compatible environment.
- **Dependency Management:** Ensuring all required libraries (e.g., requests, bs4, pandas) are installed and accessible within the Airflow environment.
- **Integration with DVC:** Setting up DVC and integrating it seamlessly into the workflow, including managing credentials and authentication for DVC operations.
- **Error Handling:** Implementing robust error handling mechanisms to manage potential issues during data extraction, transformation, and storage.

## Conclusion
This documentation outlines the data preprocessing steps and DVC setup within an Apache Airflow workflow. By following these steps and addressing potential challenges, the workflow aims to automate data management tasks effectively, ensuring data integrity, reproducibility, and version control.

