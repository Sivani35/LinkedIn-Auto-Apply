from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import os
from dotenv import load_dotenv
from datetime import datetime
import sys

# Load environment variables
load_dotenv()

class LinkedInJobApply:
    def __init__(self, status_callback=None, job_callback=None, applied_callback=None):
        self.driver = None
        self.wait = None
        self.applied_jobs = []
        self.status_callback = status_callback
        self.job_callback = job_callback
        self.applied_callback = applied_callback
        self.setup_driver()
        self.setup_logging()

    def setup_logging(self):
        """Set up logging file"""
        self.log_file = f"linkedin_applications_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        with open(self.log_file, "w") as f:
            f.write(f"LinkedIn Job Application Log - Started at {datetime.now()}\n")
            f.write("="*50 + "\n\n")

    def print_status(self, message, status="INFO"):
        """Print a formatted status message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        if status == "SUCCESS":
            print(f"\033[92m[{timestamp}] ✓ {message}\033[0m")  # Green
        elif status == "ERROR":
            print(f"\033[91m[{timestamp}] ✗ {message}\033[0m")  # Red
        elif status == "WARNING":
            print(f"\033[93m[{timestamp}] ⚠ {message}\033[0m")  # Yellow
        elif status == "PROGRESS":
            print(f"\033[94m[{timestamp}] ⟳ {message}\033[0m")  # Blue
        else:
            print(f"[{timestamp}] ℹ {message}")  # Default

    def log_message(self, message, status="INFO"):
        """Log a message to both console and file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.print_status(message, status)
        with open(self.log_file, "a") as f:
            f.write(log_entry + "\n")
        
        # Call the status callback if provided
        if self.status_callback:
            self.status_callback(message, status)

    def setup_driver(self):
        """Set up the Chrome WebDriver with appropriate options"""
        self.log_message("Setting up Chrome WebDriver...", "PROGRESS")
        chrome_options = Options()
        # chrome_options.add_argument("--headless")  # Uncomment to run in headless mode
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-notifications")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        self.log_message("Chrome WebDriver setup complete", "SUCCESS")

    def login(self):
        """Log in to LinkedIn"""
        try:
            self.log_message("Attempting to log in to LinkedIn...", "PROGRESS")
            self.driver.get("https://www.linkedin.com/login")
            
            # Enter email
            email_field = self.wait.until(EC.presence_of_element_located((By.ID, "username")))
            email_field.send_keys(os.getenv("LINKEDIN_EMAIL"))
            self.log_message("Email entered successfully", "SUCCESS")
            
            # Enter password
            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(os.getenv("LINKEDIN_PASSWORD"))
            self.log_message("Password entered successfully", "SUCCESS")
            
            # Click login button
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            # Wait for login to complete
            time.sleep(5)
            self.log_message("Successfully logged in to LinkedIn", "SUCCESS")
            return True
        except Exception as e:
            self.log_message(f"Login failed: {str(e)}", "ERROR")
            return False

    def search_jobs(self):
        """Search for business analyst internship jobs"""
        try:
            self.log_message("Navigating to LinkedIn Jobs page...", "PROGRESS")
            self.driver.get("https://www.linkedin.com/jobs/")
            time.sleep(3)
            
            # Enter search terms
            search_box = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[aria-label='Search by title, skill, or company']")))
            search_box.clear()
            search_box.send_keys("Business Analyst Intern")
            self.log_message("Search term 'Business Analyst Intern' entered", "SUCCESS")
            
            # Enter location
            location_box = self.driver.find_element(By.CSS_SELECTOR, "input[aria-label='City, state, or zip code']")
            location_box.clear()
            location_box.send_keys("United States")
            self.log_message("Location 'United States' entered", "SUCCESS")
            
            # Click search button
            search_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            search_button.click()
            self.log_message("Job search initiated", "SUCCESS")
            
            time.sleep(3)
            return True
        except Exception as e:
            self.log_message(f"Job search failed: {str(e)}", "ERROR")
            return False

    def apply_to_jobs(self):
        """Apply to jobs that match criteria"""
        try:
            self.log_message("Waiting for job listings to load...", "PROGRESS")
            job_cards = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".job-card-container")))
            self.log_message(f"Found {len(job_cards)} job listings", "SUCCESS")
            
            for index, job_card in enumerate(job_cards[:10], 1):  # Limit to first 10 jobs
                try:
                    print("\n" + "="*50)
                    self.log_message(f"Processing job {index} of 10...", "PROGRESS")
                    
                    # Get job title and company before clicking
                    job_title = job_card.find_element(By.CSS_SELECTOR, ".job-card-list__title").text
                    company_name = job_card.find_element(By.CSS_SELECTOR, ".job-card-container__company-name").text
                    self.log_message(f"Job Title: {job_title}", "INFO")
                    self.log_message(f"Company: {company_name}", "INFO")
                    
                    # Update current job in the dashboard
                    if self.job_callback:
                        self.job_callback({
                            'title': job_title,
                            'company': company_name,
                            'status': 'Processing',
                            'index': index,
                            'total': 10
                        })
                    
                    # Click on job card
                    job_card.click()
                    time.sleep(2)
                    
                    # Check if it's an internship
                    job_title = self.driver.find_element(By.CSS_SELECTOR, ".job-title").text.lower()
                    if "intern" not in job_title:
                        self.log_message("Skipping - Not an internship position", "WARNING")
                        if self.job_callback:
                            self.job_callback({
                                'title': job_title,
                                'company': company_name,
                                'status': 'Skipped - Not an internship',
                                'index': index,
                                'total': 10
                            })
                        continue
                    
                    # Check if it's in the US
                    location = self.driver.find_element(By.CSS_SELECTOR, ".job-location").text.lower()
                    if "united states" not in location and "us" not in location:
                        self.log_message("Skipping - Not in United States", "WARNING")
                        if self.job_callback:
                            self.job_callback({
                                'title': job_title,
                                'company': company_name,
                                'status': 'Skipped - Not in US',
                                'index': index,
                                'total': 10
                            })
                        continue
                    
                    # Click apply button
                    apply_button = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-control-name='jobdetails_topcard_inapply']")))
                    apply_button.click()
                    self.log_message("Clicked apply button", "SUCCESS")
                    
                    # Handle the application process
                    if self.handle_application_process():
                        job_info = {
                            'title': job_title,
                            'company': company_name,
                            'location': location,
                            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        self.applied_jobs.append(job_info)
                        
                        # Notify about successful application
                        if self.applied_callback:
                            self.applied_callback(job_info)
                        
                        if self.job_callback:
                            self.job_callback({
                                'title': job_title,
                                'company': company_name,
                                'status': 'Applied Successfully',
                                'index': index,
                                'total': 10
                            })
                    
                except Exception as e:
                    self.log_message(f"Failed to process job: {str(e)}", "ERROR")
                    continue
                
        except Exception as e:
            self.log_message(f"Job application process failed: {str(e)}", "ERROR")

    def handle_application_process(self):
        """Handle the job application process"""
        try:
            # Wait for application form to load
            time.sleep(2)
            
            # Check if it's an easy apply
            if "Easy Apply" in self.driver.page_source:
                self.log_message("Starting Easy Apply process...", "PROGRESS")
                step = 1
                
                # Click through the application steps
                while True:
                    try:
                        self.log_message(f"Processing step {step}...", "PROGRESS")
                        # Look for the next button
                        next_button = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[aria-label='Continue to next step']")))
                        next_button.click()
                        time.sleep(2)
                        step += 1
                    except TimeoutException:
                        # If no next button is found, we're at the end
                        break
                
                # Submit the application
                self.log_message("Submitting application...", "PROGRESS")
                submit_button = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[aria-label='Submit application']")))
                submit_button.click()
                time.sleep(2)
                
                # Close the confirmation dialog if it appears
                try:
                    close_button = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Dismiss']")
                    close_button.click()
                    self.log_message("Application submitted successfully!", "SUCCESS")
                except NoSuchElementException:
                    self.log_message("Application submitted successfully!", "SUCCESS")
                return True
            else:
                self.log_message("Not an Easy Apply job - skipping", "WARNING")
                return False
                
        except Exception as e:
            self.log_message(f"Application process failed: {str(e)}", "ERROR")
            return False

    def generate_summary(self):
        """Generate a summary of applied jobs"""
        print("\n" + "="*50)
        self.log_message("=== Application Summary ===", "SUCCESS")
        self.log_message(f"Total jobs applied: {len(self.applied_jobs)}", "SUCCESS")
        for job in self.applied_jobs:
            print("\n" + "-"*30)
            self.log_message(f"Job: {job['title']}", "INFO")
            self.log_message(f"Company: {job['company']}", "INFO")
            self.log_message(f"Location: {job['location']}", "INFO")
            self.log_message(f"Applied at: {job['timestamp']}", "INFO")
        print("\n" + "="*50)

    def close(self):
        """Close the browser and generate summary"""
        self.generate_summary()
        if self.driver:
            self.driver.quit()
            self.log_message("Browser closed", "INFO")

def main():
    print("\n=== LinkedIn Job Application Bot ===")
    print("Starting automated job application process...\n")
    
    bot = LinkedInJobApply()
    try:
        if bot.login():
            if bot.search_jobs():
                bot.apply_to_jobs()
    finally:
        bot.close()

if __name__ == "__main__":
    main() 