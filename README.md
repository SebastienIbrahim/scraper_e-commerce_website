# Cdiscount Scraper Project
Welcome to the Cdiscount Scraper project README. This project is designed to scrape product information from the Cdiscount e-commerce website. Below, you will find comprehensive information on the project's structure, functionality, and how to use it effectively.

# Project Overview
The project is organized into several directories and files, each serving a specific purpose. Here's a brief overview of the project's structure:

# Project Structure
* Cdiscount: Main directory for storing scraped data and URLs.
  * raw_data: Directory for storing raw scraped data.
  * shop_urls: Directory for storing shop URLs.
* utils: Contains utility modules for the project.
  * configs.py: Configuration module to manage project settings.
  * desktop_config.yml: YAML configuration file for desktop scraping settings.
  * mobile_config.yml: YAML configuration file for mobile scraping settings.
  * poppup.py: Module for displaying popup messages.
* scraper.py: Main script for initiating the scraping process.
* model.py: Module containing classes for managing the web driver, website information, and crawling logic.
* parse_data.py: Module for parsing and extracting information from the scraped pages.
* requirements.txt: List of required Python dependencies for the project.
* README.md: This README file.

# Main Files
* scraper.py: Main entry point for initiating the scraping process.
* model.py: Module containing classes for managing the web driver, website information, and crawling logic.
* parse_data.py: Module for parsing and extracting information from the scraped pages.
* requirements.txt: List of required Python dependencies for the project.
* README.md: This README file.

# Project Functionality
This project serves the following main functions:

* Web Scraping: Utilizes web scraping techniques to collect product information from the Cdiscount website. Configurations for each website are stored in the configs.py and YAML files within the utils/ directory.
* Crawling Logic: Implements crawling logic to navigate through the website, visiting target pages and extracting relevant information.

# Using the Project
To use this project effectively, follow these steps:

* Install Dependencies: Ensure that you have the required Python dependencies installed. You can install them using pip with the command pip install -r requirements.txt.
* Configure the Project: Customize the project's configuration settings in the configs.py file and the YAML configuration files in the utils/ directory to meet your specific requirements.
* Run the Project: Execute the project by running python scraper.py. This initiates the web scraping process for the Cdiscount website, and the scraped data is stored in the Cdiscount/ directory.
* Data Parsing: The project automatically parses the scraped data, extracting relevant information from the pages.
* Error Handling: In case of issues or errors during web scraping, refer to the log files located in the main project directory (geckodriver.log, logs.log) for detailed error information.

Feel free to explore and adapt the project's codebase to suit your specific requirements or use cases. Additional documentation for individual modules and functions can be found within the project's source code files.
