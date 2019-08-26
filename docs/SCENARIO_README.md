### Example Usage

Below is an example scenario to demonstrate the usage of CCAT. 

Starting with compromised AWS credentials, the attacker enumerates and explores ECR repositories. Then, the attacker found that they use NGINX Docker image and pulled that Docker image from ECR. Furthermore, the attacker creates a reverse shell backdoor into the target Docker image. Finally, the attacker pushes the backdoored Docker image to ECR.

#### Exploitation Route:
![CCAT](/docs/images/ccat_scenario_diagram.png)

#### Exploitation Route Walkthrough with CCAT:

1. The attacker explores the AWS environment and discovers they are able to list ECR repositories using compromised AWS credentials.

    * Enumerate ECR repositories
      
      ![CCAT](/docs/images/scenario/ccat_enum_ecr.png)

      * Configure AWS CLI Profile

        > The first time CCAT is launched, the attacker will be prompted to configure their AWS CLI profile. This profile will be used to run the related AWS attack modules.
        
        ![CCAT](/docs/images/scenario/ccat_aws_profile_configure_1.png)

      * Then the attacker selects target AWS regions
        
        ![CCAT](/docs/images/scenario/ccat_enum_repos_regions.png)

    * Then the attacker lists enumerated ECR repositories with simple table format
      
      ![CCAT](/docs/images/scenario/ccat_list_repos_1.png)
      
      ![CCAT](/docs/images/scenario/ccat_list_repos_2.png)

2. The attacker finds that they use the NGINX Docker image and pulls that Docker image from ECR.
    
    * Pull ECR repository

      ![CCAT](/docs/images/scenario/ccat_pull_repo_menu.png)

      * Then there are two options to pull from ECR repositories so the attacker chooses a single repository with multiple tags option 
      
        ![CCAT](/docs/images/scenario/ccat_pull_repo_options.png)
      
      * Then the attacker will be promoted to provide AWS region, ECR repository URI, repository tags
      
        ![CCAT](/docs/images/scenario/ccat_pull_single_repo.png)

3. The attacker decides to create a reverse shell backdoor into the pulled NGINX Docker image.    
    
    * The attacker starts a listener for reverse shell

      ![CCAT](/docs/images/scenario/reverse_shell_listener.png)
    
    * Then the attacker creates a reverse shell backdoor

      > This module generates a Dockerfile on the fly and builds new a Docker image.

      ![CCAT](/docs/images/scenario/docker_backdoor_menu.png)
    
      * Then the attacker will be promoted to provide repository name, tag and new build tag  

        ![CCAT](/docs/images/scenario/docker_backdoor_repo_info.png)
      
      * Then the attacker generates a Dockerfile, adds reverse shell configuration, and overwrites the default CMD command

        > "CMD sets default command and/or parameters, which can be overwritten from command line when docker container runs."

        ![CCAT](/docs/images/scenario/docker_backdoor_dockerfile.png)
      
      * Then the attacker reviews a Dockerfile and builds new backdoored NGINX Docker image

        ![CCAT](/docs/images/scenario/docker_backdoor_dockerfile_review_build.png)

    * Then the attacker tests the backdoored Docker image 

        * Run a backdoored container
      
          ![CCAT](/docs/images/scenario/reverse_shell_test_run_container.png)
        
        * Test NGINX server

          ![CCAT](/docs/images/scenario/reverse_shell_test_nginx_part.png)

        * Test reverse shell backdoor

          ![CCAT](/docs/images/scenario/reverse_shell_test_listener.png)

4. Finally, the attacker pushes the backdoored Docker image to ECR.

      * Check AWS Web Console BEFORE pushing the backdoored Docker image

        ![CCAT](/docs/images/scenario/ecr_push_repo_before.png)
      
      * Push the backdoored Docker image

        ![CCAT](/docs/images/scenario/ccat_push_menu.png)
      
        * The attacker will be promoted to provide AWS region, ECR repository URI and repository tag

          ![CCAT](/docs/images/scenario/ccat_push_repo_info.png)

      * Check AWS Web Console AFTER pushing the backdoored Docker image

        ![CCAT](/docs/images/scenario/ccat_push_repo_after.png)