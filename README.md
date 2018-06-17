# QUIC-Test-Framework

QUIC Test Framework currently pulls the below implementation of IETF QUIC from the respective repositories and builds it. 

1. picoquic
2. ngtcp2
3. quicly 

After building the implementations, it also runs 2 tests with picoquic as server and ngtcp2 and quicly as client. The logs collected from the above tests are parsed using LogParser.py and the results are published using HTML publisher in Jenkins. This feature is not complete currently some random results are published 

Follow the steps below to setup Jenkins server in your local machine
1. Download the latest release of Jenkins from their home page https://jenkins.io/.
2. Once the jenkins is up, it can be accessed at http://localhost:8080
3. Install the following Jenkins Plugin from "Manage Plugins" in "Manage Jenkins"
    - Build Pipeline Plugin
    - CMake Plugin
    - GIT Plugin
    - HTML Publisher Plugin
    - Workspace Cleanup Plugin
4. To create a new job, select "New Item" and choose the project type as "Pipeline"
5. In the Advanced Project Options, either select Pipeline script in the drop down and then copy&paste the JenskinsScript content 
or, select pipeline script from SCM, fill the repository URL, credentials and also change the Script Path from Jenkinsfile to JenkinsScript.
6. To build the jenkins project click Build Now.  
