import pytest
from flask_testing import TestCase
from app import app

class MyTest(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        return app

    def test_hello(self):
        response = self.client.get('/')
        self.assert200(response)
        self.assertEqual(response.data.decode(), "Hallo Welt!")

    def test_hello_name(self):
        response = self.client.get('/hello/Max')
        self.assert200(response)
        self.assertEqual(response.data.decode(), "Hallo, Max!")

    def test_data(self):
        response = self.client.get('/data')
        self.assert200(response)
        self.assertEqual(response.json, {'key': 'value', 'int': 1})

    def test_post_data(self):
        response = self.client.post('/post', json={'name': 'Tester'})
        self.assertStatus(response, 201)  
        self.assertEqual(response.json, {'name': 'Tester'})

if __name__ == '__main__':
    pytest.main()
