from modules import DataHub

apiObj = DataHub.API()
Patient_Location = apiObj.GetPatient('P001')[0]
print(Patient_Location)