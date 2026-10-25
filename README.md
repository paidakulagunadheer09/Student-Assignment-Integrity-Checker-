\# Student Assignment Submission Integrity Checker



A Python and Streamlit application that uses Cyclic Redundancy Check (CRC) algorithms to detect accidental modification or corruption of student assignment files.



\## Features

\- Submit assignment files with student details.

\- Generate CRC values using CRC-3, CRC-4, and CRC-8.

\- Store submission records locally in JSON format.

\- Verify a file by comparing its current CRC with the stored CRC.

\- Identify whether CRC values match or differ.



\## Technologies Used

\- Python

\- Streamlit

\- JSON

\- CRC algorithms



\## Installation



1\. Install Python.

2\. Clone or download this repository.

3\. Open a terminal in the project folder.

4\. Install dependencies:



&#x20;  `pip install -r requirements.txt`



5\. Run the application:



&#x20;  `streamlit run app.py`



\## How It Works



The application calculates a CRC value for an uploaded assignment and stores that value as a reference. During verification, it calculates the CRC again and compares the result with the stored value.



\- Matching CRC values: No error detected.

\- Different CRC values: Error detected.



\## Limitations



CRC is an error-detection mechanism, not a cryptographic security guarantee. CRC-3, CRC-4, and CRC-8 have small output spaces and can produce collisions.



\## Project Type

Academic project for Operating Systems coursework.



