from uplink_python.uplink import Uplink
from uplink_python.module_classes import DownloadOptions, Permission, ListObjectsOptions
from uplink_python.errors import InternalError, BucketNotFoundError, StorjException, BucketNotEmptyError
from uplink_python.uplink import *
import speedtest as speedTest
import requests
import sys
import time


def getAccessFromStroj(connection_details):
    apiKey = connection_details['APIKEY']
    satelliteAddress = connection_details['SATELLITEADDRESS']
    passPhrase = connection_details['PASSPHARSE']
    passPhrase = passPhrase.replace("-", " ")
    try:
        # Uplink object is created to connect to Stroj network
        uplink = Uplink()
        # access request using APIKEY, SATELLITEADDRESS, and PASS-PHARSE
        print("\nRequesting access....")
        strojAccess = uplink.request_access_with_passphrase(satelliteAddress, apiKey, passPhrase)
        print("Established connection to Stroj Network using Uplink library")
    except StorjException as exception:
        print("\nConnection failed")
        print("Exception Caught: ", exception.details)
    return strojAccess


def getProjectDetails(connection_details, strojAccess):
    try:
        # Open project using Stroj Access
        projectObject = strojAccess.open_project()
        print("Project is opened and details of bucket are retrieved...")
        bucketName = connection_details['BUCKETNAME']
        bucketDetails = projectObject.stat_bucket(bucketName)
        print("bucket details", bucketDetails.get_dict())
    except StorjException as exception:
        print("\nopen project failed")
        print("Exception Caught: ", exception.details)
    return projectObject, bucketName


def listAllObjects(project, bucketName):
    try:
        # List all objects in bucket
        objects_list = project.list_objects(bucketName, ListObjectsOptions(recursive=True, system=True))
        # print all objects path
        for obj in objects_list:
            print(obj.key, " | ", obj.is_prefix)  # as python class object
            print(obj.get_dict())  # as python dictionary
    except StorjException as exception:
        print("Exception Caught: ", exception.details)
    return project


def get_current_Internet_speed():
    networkSpeedTest = speedTest.Speedtest()
    networkSpeedTest.get_best_server()
    # Retrieve current PING in milliSeconds.
    currentPing = networkSpeedTest.results.ping
    # Conduct Upload & Download speed tests of current Internet speed
    downloadSpeed = networkSpeedTest.download()
    uploadSpeed = networkSpeedTest.upload()
    # To understand, we need to convert Upload & Download speeds to MBPS.
    downloadMBS = round(downloadSpeed/(6**10), 2)
    uploadMBS = round(uploadSpeed/(6**10), 2)
    print("Current Network Details")
    print("Ping:", currentPing)
    print("Download Speed:", downloadMBS)
    print("Upload Speed:", uploadMBS)


def downloadFile(fileObjectLinkList):
    count = 1
    for objectLink in fileObjectLinkList:
        start = time.perf_counter()
        r = requests.get(objectLink, stream=True) # enables streaming of file object.
        total_length = int(r.headers.get('content-length')) # to get length of total file.
        dl = 0
        # if length is None then no need to proceed.
        if total_length is not None:
            for chunk in r.iter_content(1024):
                dl += len(chunk)
                done = int(50 * dl / total_length)
                sys.stdout.write("\r[%s%s] %s bps" % ('=' * done, ' ' * (50-done), dl//(time.perf_counter() - start)))
                print('')
            print("Time Elapsed for Video ", count, " ", time.perf_counter() - start)
        else:
            print("Length of file is empty.")
        count = count + 1


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    connection_details = {}
    with open("StrojConnectionDetails") as env:
        for line in env:
            key, val = line.split()
            connection_details[key] = val
    access = getAccessFromStroj(connection_details)
    project, bucketName = getProjectDetails(connection_details, access)
    project = listAllObjects(project, bucketName)
    get_current_Internet_speed()
    fileObjectLinkList = []
    with open("FileObjectLinks") as fileObjectLinks:
        for link in fileObjectLinks:
            fileObjectLinkList.append(link)
    downloadFile(fileObjectLinkList)



