import json, subprocess
import threading

# Placeholder - needs moving to some .env file but problems with my venv
account_id='111111111111'
region='eu-west-2'

def initiate_vault_job():
    """
    Step 1 - Send initiate request for each vault name specified in the array.
    Output: result.json - contains a JSON object of all vaults (keys) with corresponding jobids (values)
    """
    json_parsed = ["YourVaultName1","YourVaultName2"]
    
    jobs = {}
    for vaultname in json_parsed:
        command = "aws glacier initiate-job --account-id " + account_id + " --job-parameters '{\"Type\": \"inventory-retrieval\"}' --vault-name " + vaultname + " --profile p2"
        res = subprocess.run(command, shell=True, check=True, capture_output=True)
        outp = res.stdout.decode('utf-8')
        
        jobs[vaultname] = outp[7:99]
        jobiD = outp[7:99]

    with open('result.json', 'w') as fp:
        json.dump(jobs, fp)




def job_status_check():
    """
    Step 2 - Send requests to check is the jobids request outputs ("retrieve inventory") are available on AWS to be downloaded
    Output: None
    """

    with open('result.json') as f:
        json_parsed = json.load(f)
    for vaultname, jobid in json_parsed.items(): 
        command = "aws glacier describe-job --account-id 762825116798 --profile p2 --job-id " + jobid + " --vault-name " + vaultname
        # print("command is: " + command)
        res = subprocess.run(command, shell=True, check=True, capture_output=True)

        if res.returncode == 0:
            outp = res.stdout.decode('utf-8')
            print("Response from AWS: " + outp )
        else:
            print("Failed for vault: " + vaultname )





def download_vault_inventory():
    """
    Step 3 - Once the inventories are availabe, download each into a file <vaultname>.json
    Output: ./json/<vaultname>.json files
    """
    with open('result.json') as f:
        json_parsed = json.load(f)

    i = 0
    vaults = list(json_parsed.keys())

    while i < len(vaults):
        command = "aws glacier get-job-output --account-id 762825116798 --vault-name " + vaults[i] + " --job-id " + json_parsed[ vaults[i] ] + " --profile p2 ./json/" + vaults[i]+ ".json"
        # print("command is: " + command)
        res = subprocess.run(command, shell=True, capture_output=True)

        if res.returncode == 0:
            print("Downloaded achive list for vault " +  vaults[i] +  " (" +str(i+1)+ "/" + str(len(vaults)) + ")"  )
            i += 1
        else:
            print("Failed for vault " +  vaults[i] + ". Trying again..." )





def delete_archives():
    """
    Step 4 - For each vault, iterate through it's <vaultname>.json and send delete each archive in turn
    Output: None.
    """
    with open('result.json') as f:
        json_parsed = json.load(f)

    threads = list()
    for vaultname, jobid in json_parsed.items(): 
        x = threading.Thread(target=empty_vault, args=(vaultname,))
        threads.append(x)
        x.start()
        # empty_vault(vaultname)
    
    print("***FINISHED*** \nAll provided vaults are now empty!")


def empty_vault(vaultname):
    with open("./json/" + vaultname + ".json") as f:
        archives_json = f.read()

    archive_list = json.loads(archives_json)['ArchiveList']
    # archive_list = parsed_json[
    print("EMPTYING VAULT: " + vaultname + "...")

    i = 0
    while i < len(archive_list):
        command = "aws glacier delete-archive --archive-id=\"" + archive_list[i]['ArchiveId'] + "\" --vault-name " + vaultname + " --account-id " + account_id + " --profile p2 --region " + region
        res = subprocess.run(command, shell=True, check=True, capture_output=True)
        if res.returncode == 0:
            print(vaultname + ": Deleted archive (" +str(i+1)+ " of " + str(len(archive_list)) + ")" + archive_list[i]['ArchiveId'])
            i += 1
        else:
            print(vaultname + "Trying again... (" + str(i) )

    print(vaultname + "All achives deleted! Vault now empty")