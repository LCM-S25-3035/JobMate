#!/usr/bin/env python3
"""
Test for one-click application feature
"""

import os
import sys
from flask import Flask, session, url_for
from flask_login import current_user
from app import create_app, db
from app.models.user import User
from bson import ObjectId
import unittest
from unittest.mock import patch, MagicMock
import json


class ApplicationFeatureTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.app = create_app('testing')
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['TESTING'] = True
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        
        # Create a test user and mock data
        user = User(username='testuser', email='test@example.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        
        # Mock MongoDB job data
        self.mock_job = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "title": "Software Engineer",
            "company": "Test Company",
            "description": "Test job description",
            "job_url_direct": "https://example.com/apply",
            "application_email": "jobs@example.com"
        }
        
        # Login the test user
        self.client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'password'
        }, follow_redirects=True)
        
    def tearDown(self):
        """Clean up after tests"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    @patch('app.main.routes.smtplib.SMTP')
    @patch('app.main.routes.current_app')
    def test_send_application(self, mock_app, mock_smtp):
        """Test sending an application via email"""
        # Mock MongoDB connection and find_one result
        mock_app.mongo_db.jobs.find_one.return_value = self.mock_job
        mock_app.config.get.side_effect = lambda key, default=None: {
            'TESTING': True,
            'SMTP_SERVER': 'smtp.example.com',
            'SMTP_PORT': 587,
            'SMTP_USER': 'test@example.com',
            'SMTP_PASSWORD': 'password'
        }.get(key, default)
        
        # Mock MongoDB insert_one
        mock_app.mongo_db.applications.insert_one.return_value = None
        
        # Test data
        test_data = {
            'resume_text': 'Test resume content',
            'cover_letter_text': 'Test cover letter content'
        }
        
        # Send application request
        response = self.client.post(
            f'/send-application/{self.mock_job["_id"]}', 
            json=test_data,
            content_type='application/json'
        )
        
        # Assert response
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIn('Application sent successfully', data['message'])
        
        # Verify application was recorded
        mock_app.mongo_db.applications.insert_one.assert_called_once()


if __name__ == '__main__':
    unittest.main()
