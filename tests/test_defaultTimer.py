from configuration import configHandler
from diskOperations import timeFileManager
from diskOperations import fileAndFolderOperations
from tests import commonFunctions


# class TestDefaultTimer:                
#     def test_processingSingleLineOfDataInTimefile(self):#error happened once when the program didn't have a condition to handle a single line of data
#         fileFolderOps = fileAndFolderOperations.FileOperations()
#         comFunc = CommonTestFunctions()
#         #dummyTime = common.DummyTimeFunctions()        
#         archiveFolder = comFunc.createNewTestFolder(fileFolderOps)  
#         #---prime the timeFileManager with whatever parameters you want
#         tm = timeFileManager.TimeFileManager(archiveFolder, configHandler.Names.TIME_FILE, fileFolderOps)

