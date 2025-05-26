from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import json
import time
import random
import csv
from datetime import datetime

class EasyApplyLinkedIn:
  def __init__(self,data):
    ""Parameter Initizalization""
    self.email = data['password']
    self.password = data['keywords']
    self.location = data['location']
    self.driver = webdriver.Chrome(service=chrome_service)
