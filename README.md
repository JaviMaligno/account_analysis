# Bank Statement Analysis Application

This application provides an interactive interface to analyze your bank statements. By uploading your bank statements in CSV format, you can visualize and explore your income, expenses, net changes, and more over time.

## Features

- **Upload Multiple CSV Files**: Supports uploading multiple bank statement CSV files simultaneously.
- **Data Filtering**: Filter data based on custom date ranges.
- **Interactive Visualizations**: Generate plots for end-of-month balances, net changes, cumulative net changes, percentage changes, and monthly income and expenses.
- **Data Adjustments**: Optionally adjust data by removing specific transactions (e.g., currency conversions).
- **Detailed Data Tables**: View comprehensive data tables for all calculations and analyses.

## Requirements

- **Docker**
- **Docker Compose**

## Getting Started

### Running the Application with Docker Compose

1. **Clone the Repository**

   Navigate to your desired directory and clone the repository:

   ```bash
   git clone https://github.com/JaviMaligno/account_analysis.git
   cd account_analysis
   ```

2. **Build and Run the Docker Container**

   Use Docker Compose to build the image and run the container:

   ```bash
   docker-compose up --build
   ```

   This command will:

   - Build the Docker image as defined in the `dockerfile`.
   - Start the Streamlit application on port `8501`.

3. **Access the Application**

   Open your web browser and go to:

   ```
   http://localhost:8501
   ```

### Usage

1. **Upload CSV Files**

   - Click on the "Browse files" button in the application interface.
   - Select one or more CSV files containing your bank statements.

   **Note**: The CSV files should have the following columns:

   - `Date`: Transaction date in `DD-MM-YYYY` format.
   - `Description`: Description of the transaction.
   - `Amount`: Transaction amount (positive for credits, negative for debits).
   - `Running Balance`: Account balance after the transaction.

2. **Set Display Options**

   In the sidebar:

   - **Display Options**:
     - **Show Income**: Display income data.
     - **Show Expenses**: Display expenses data.
     - **Show Data Tables**: Display detailed data tables.
   - **Filter Options**:
     - **Start Date**: Select the start date for filtering.
     - **End Date**: Select the end date for filtering.

3. **View Analyses and Plots**

   The application will display:

   - **End-of-Month Balance Evolution**: Line plot showing the balance at the end of each month.
   - **Net Change**: Line plot of monthly net changes in account balance.
   - **Cumulative Net Change**: Line plot of the cumulative net change over time.
   - **Percentage Change**: Line plot of month-over-month percentage changes in balance.
   - **Monthly Income and Expenses**: Bar chart of monthly income and expenses.
   - **Averages**: Display average net change, income, and expenses.

4. **View Data Tables**

   If "Show Data Tables" is checked, detailed data tables for all calculations will be displayed below the plots.

## Customization

- **Adjustments**:

  - The application includes functions to adjust data by removing specific transactions (e.g., those containing "GBP to" in the description).
  - Adjustments are currently disabled by default. To enable data adjustments, set `show_adjusted = True` in `main.py` or modify the application to include a checkbox in the sidebar.

- **TODOs**:

  The application has pending enhancements listed in the comments of `main.py`:

  - Allow for different currencies and automate currency conversion.
  - Support different date granularities (e.g., daily, weekly).
  - Add more plots and detailed data about expenses.
  - Integrate with a database to store and retrieve data.

## File Structure

- `main.py`: The main application file containing the Streamlit app logic.
- `docker-compose.yaml`: Configuration file for Docker Compose to build and run the container.
- `dockerfile`: Dockerfile specifying the environment and how to run the application.
- `README.md`: Documentation file (this file).

## Built With

- **[Streamlit](https://streamlit.io/)**: An open-source app framework for Machine Learning and Data Science teams.
- **[Pandas](https://pandas.pydata.org/)**: A powerful data analysis and manipulation library for Python.
- **[Matplotlib](https://matplotlib.org/)**: A plotting library for creating static, animated, and interactive visualizations.
- **[NumPy](https://numpy.org/)**: A fundamental package for scientific computing with Python.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Appreciation to the developers and contributors of Streamlit, Pandas, Matplotlib, and NumPy for providing the tools utilized in this application.
