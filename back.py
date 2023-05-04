import subprocess

class ImageProccessing(object):
    hosts = ['ub1', 'ub2', 'ub5']
    # return a list of strings with the names of the hosts that are connected to the master node
    def getHostsConnected(self):

        for host in self.hosts:
            try:
                # timeout after 5 seconds to avoid delays
                result = subprocess.run(["ssh", host, "hostname"], capture_output=True, text=True, timeout=5)

            except subprocess.CalledProcessError:
                print("Exception: error running subprocess to test ssh connections")
                # stop all ssh connections
            except subprocess.TimeoutExpired:
                print("Connection with host " + host + " timed out")
                self.hosts.remove(host)
            else:
                # if the return code is 0, the connection was successful
                if result.returncode == 0: 
                    print("SSH connection to " + host + " was successful!")
                else: 
                    print("SSH connection to " + host + " failed.")
                    self.hosts.remove(host)


    def getHostsStatus(self): # Get hosts status
        self.getHostsConnected() # Get hosts connected
        # return a list of 3 elements, each element is 1 if the host is connected, 0 otherwise
        activeHosts =  len(self.hosts)
        if activeHosts == 0:
            return [0, 0, 0]
        elif activeHosts == 1:
            return [1, 0, 0]
        elif activeHosts == 2:
            return [1, 1, 0]
        elif activeHosts == 3:
            return [1, 1, 1]
        else:
            return [0, 0, 0]

    def runImageProcessing(self, numImages, imagePath):
        # check if the image path is correct
        commandLine = "mpiexec -n " + str(numImages) + " -host " + ','.join(self.hosts) + " ./mpi " + imagePath 

        try: # run the command line and get the output 
            result = subprocess.run([commandLine], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) # run the command line
            print(commandLine)
            print(result.stdout)
            if result.returncode == 0: # if the return code is 0, the connection was successful
                print(result.stdout)
                return True
            else: # if the return code is not 0, the connection failed
                print(result.stderr)
                return False
        except subprocess.CalledProcessError: # if the subprocess failed
            print(result.stderr) # print the error
            return False
        else: 
            print(result.stderr)
            return False



    # starts image processing
    def initImageProcessing(self, numImages, imagePath):
        # check if the image path is correct
        print(numImages, imagePath) 
        isSuccesful = self.runImageProcessing(numImages, imagePath) # run the image processing
        imagesToDisplay = [] # list of images to display
        if isSuccesful: # if the image processing was succesful 
            imagesToDisplay = [f"blurred_{i}.bmp" for i in range(1, numImages + 1)] # add the images to the list
        else: # if the image processing failed
            imagesToDisplay = [imagePath] # add the original image to the list

        print(imagesToDisplay) # print the list of images to display
        
        return imagesToDisplay # return the list of images to display



# send image path with this format
# initImageProcessing(3, './f4.bmp')
# back = ImageProccessing()
# back.getHostsStatus()
# back.initImageProcessing(3, './images/f4.bmp')