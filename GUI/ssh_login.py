import paramiko

ssh_client = paramiko.SSHClient()

def login(user_name, password):
    try:
        host_address = "192.168.140.46"
        # add remote server to known_host if connecting for the first time
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=host_address, username=user_name, password=password)
        return True
    except:
        return False

# open sftp connection

#sftp_client = ssh_client.open_sftp()

# to download a file from remote server to local machine
#sftp_client.get("from_location", "to_location")

# to upload a file from local machine to remote server
#sftp_client.put("from_location", "to_location")


# stdin, stdout, stderr = ssh_client.exec_command("ls -lrth")

#sftp_client.get("/tb/shared/akash.kini/pythonScripts/LogChecker/temp_file.txt", "temp_file_downloaded.txt")

# close sftp client
#sftp_client.close()
# close ssh client
ssh_client.close()