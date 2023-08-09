import generate_actions as actions
import requests
import numpy as np
import urllib.parse
import re
import random
import sys
#import const

class SQLi_Environment():

    def __init__(self, url, verbose=True, flag_reward = 10, query_reward = -1, exploit_query_reward = -50):
        print("Init Env SQLi_Environment")
        self.actions = np.array(actions.generate_actions(None , 3))
        self.query_reward = query_reward

        self.exploit_query_reward = exploit_query_reward
        self.flag_reward = flag_reward
        self.termination = False
        self.verbose = verbose
        self.url = url

    def step(self, action):
        """
        Posts a payload on the server, analyzes the response, then returns
        the reward/punishment together with other necessary info

        Returns a tuple of:
        status code (int), reward (int), termination (boolean ), debug string (string)
        """
        status = self.test_HTTP_connection()
        if status == -1:
            return

        response = self.post_payload(self.actions[action])

        reward = self.query_reward
        #adding extra punishment if agent uses exploit payloads
        if len(self.actions) > 30:
        #means a filter based list
            if action > 30:
                #every action after index 30 are exploit payloads
                reward = self.exploit_query_reward
        elif(action >= 18):
        #Agent is trying an exploit payload in the normal payload list
            reward = self.exploit_query_reward

        result = self.analyze_response(response)


        if result == -1: ##somehow got output from query but no flag (should not happen)
            return -1, reward, self.termination,'Server result is -1'
        elif result == 0: #server error
            return 0, reward, self.termination,'Server result is 0'
        elif result == 1: #illegal character
            return 1, reward,self.termination,'Server result is 1'
        elif result == 2: #empty response
            return 2, reward,self.termination,'Server result is 2'
        elif result == 3: #found flag
            self.termination = True
            return 3, self.flag_reward,self.termination,'Server result is 3'
        else:
            print("ERROR")
            return

    def test_HTTP_connection(self):
        #confirm that the environment is running
        response = requests.get(self.url)
        if response.status_code != 200:
            if self.verbose:
                print(f"Environment is not running. Error status {response.status_code}")
            sys.exit()
        else:
            if(self.verbose):
                print(f"Environment is up and running")


    def post_payload(self, action):
        """
        Takes an action from the action list and uses it as a
        payload on the server


        action: The payload string which is posted on the website
        """
        if self.verbose:
            print(f"SQL Query is: {action}")
        #perform injection
        forms = {
            'name': 'test',
            'email': action
        }
        response = requests.post(self.url, data = forms)
        return response

    def analyze_response(self, response):
        """
        Takes a response element and determines
        whether the query was successful or not

        Returns a status code between -1 and 3
        """
        response = response.text
        returned_rows = response.find("Returned rows are:")
        if returned_rows != -1: #did not break query - correct escape/syntax
            if "{Flag}" in response:
                if self.verbose:
                    print("FOUND FLAG")
                return 3
            elif response.find("Returned rows are: 0") != -1:
                #wrong escape
                if self.verbose:
                    print("Wrong escape for query")
                return 0
            else:
                if self.verbose:
                    print("Successfull query, but no flag")
                return 1

        elif returned_rows == -1: #broke query, which means illegal syntax
            if self.verbose:
                print("Illegal character. Correct escape for query(?)") ##Can possibly crash for other reasons as well
            return 2
        else:
            if self.verbose:
                print("This should never be printed out") ##at least with the current setup
            return -1

    def reset_website(self, type):
        """
        Changes the vulnerable SQL query on the server from a predefined
        list of queries

        type (int): type of SQLi challenge on the server
        1: stack_based
        2: union_based
        3: stack_filter_based
        4: union_filter_based
        """

        print("Env reset_website type:" + str(type))

        if type == 5:
            #randomizing the type of query for every episode
            #1/2 for index page with or without WAF
            #1/2 for union based or stack based SQLi for each of the index pages
            type = random.randint(1,4)

        if(type == 1):
            path = "stack_based"
        elif(type == 2):
            path = "union_based"
        elif(type == 3):
            path = "stack_filter_based"

        elif(type==4):
            path = "union_filter_based"
        else:
            print("ERROR")
            return

        self.url = f"http://localhost/websqli/{path}/index.php"
        requests.get(f"http://localhost/websqli/{path}/new_episode.php")

    def reset(self, type):
        """
        Resets all parameters
        """
        print("Env reset type:" + str(type))
        self.termination = False
        self.reset_website(type)
        return None, 0, self.termination, 'Game reset'