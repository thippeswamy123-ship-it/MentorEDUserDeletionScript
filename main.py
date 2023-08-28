import argparse
import os
import sys
import json
import time
import requests
import csv
from configparser import ConfigParser, ExtendedInterpolation

config = ConfigParser(interpolation=ExtendedInterpolation())
config.read('common_config/config.ini')

#Below function is used to check the input file is in csv format or not
def valid_file(param):
    base, ext = os.path.splitext(param)
    if ext.lower() not in ('.csv'):
        raise argparse.ArgumentTypeError('File must have a csv extension')
    return param

# creating the parser arguments
parser = argparse.ArgumentParser()
parser.add_argument('--env', required=True, help='Specify the environment')
parser.add_argument('--inputCsvFile', '--inputCsvFile', type=valid_file)
argument = parser.parse_args()
environment = argument.env
inputCsvFile = csv.DictReader(open(argument.inputCsvFile, 'rt'))

# Below function is used for environment check
def envCheck(environment):
    try:
        config[environment]
        return True
    except Exception as e:
        print(e)
        return False

# Below function is used to give the termination msg
def terminatingMessage(msg):
    print(msg)
    sys.exit()

# Cross checking the environment if not valid it wil give error as in else part
if envCheck(environment):
    print("=================== Environment set to " + str(environment) + " =====================")
else:
    terminatingMessage(str(environment) + " is an invalid environment")

#This function is used to generate the access token
def generateAccessToken():
    try:
        loginapibody = {
            'email': config.get(environment,'email'),
            'password': config.get(environment,'Password')
        }
        responseKeyClockUser = requests.post(url=config.get(environment, 'UserDevBaseUrl') + config.get(environment, 'login'), data=loginapibody)
        
        if responseKeyClockUser.status_code == 200:
            print("-------->Access token gereated successfully<--------")
            responseJson = responseKeyClockUser.json()
            accessTokenUser = responseJson['result']['access_token']
            return accessTokenUser
        else:
            print("Error in generating Access token")
            

    except requests.exceptions.RequestException as e:
        print("Exception during API request:", e)
        terminatingMessage("An error occurred during Access Token generation.")


if __name__ == "__main__":
    access_token = generateAccessToken()

# this function is used to delete the user for mentoruser side
def mentoruserdeletion(requestedID, access_token):
    headerKeyClockUser = {'X-auth-token': "bearer " + access_token}
    mentoreuserurl = config.get(environment, 'UserDevBaseUrl') + config.get(environment, 'mentoreduser') + str(requestedID)
    print("-------->mentorED user deletion user API calling<--------")
    
    responsementoruerdel = requests.post(url=mentoreuserurl, headers=headerKeyClockUser)
    return responsementoruerdel
# this function is used to delete the user for mentoruser mentoring side
def mentormentoringdeletion(requestedID, access_token):
    headerKeyClockUser = {'X-auth-token': "bearer " + access_token}
    mentoreuserurl = config.get(environment, 'MentoringBaseUrl') + config.get(environment, 'mentoring') + str(requestedID)
    print("------->mentorED mentoring deletion user API calling<-------")
    
    responsementoruerdel = requests.post(url=mentoreuserurl, headers=headerKeyClockUser)
    return responsementoruerdel
# creating empty list 
output_data = []

#iterating the requestedID
for row in inputCsvFile:
    requested_id = row['requestedID']

    # here we are calling the 2 functions which we defined and storing in respecting variable's
    mentor_user_response = mentoruserdeletion(requested_id, access_token)
    mentor_mentoring_response = mentormentoringdeletion(requested_id, access_token)
    
    # Store response data in output_data list
    if mentor_mentoring_response.status_code and mentor_user_response.status_code == 200:
        print("------>mentorED user deletion success <------")
        print("------->mentorED mentoring deletion success< ------")
        output_data.append([
            requested_id,mentor_user_response.text ,mentor_mentoring_response.text ,
            print("---------->Execution completed. Output saved in outPutFile<--------")
        ])
    else:
        print("------->ERROR : please cross check the UUID which you have provided<-------")

# Write output_data to output CSV file
output_csv_filename = 'outPutFile.csv'
with open(output_csv_filename, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["requestedID", "mentorUserResponse", "mentorMentoringResponse"])
    writer.writerows(output_data)

