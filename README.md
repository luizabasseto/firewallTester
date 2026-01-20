# Firewall Tester

This software was developed to enhance network security through practical and efficient firewall testing. More than just a testing tool, it serves as a valuable educational resource, designed to simplify and improve the learning process about firewalls. With an intuitive and interactive interface, students can visualize and experiment with firewall rule creation and application, making complex concepts easier to understand and fostering deeper, more effective learning.

The software enables the creation of network scenarios using [GNS3](https://www.gns3.com/). Hosts within the scenario should utilize Docker images to create containers for firewall testing (this version of the software supports only containers). Once the network scenario is set up in GNS3 and all hosts are powered on, you can launch the firewall rule testing software on the host running the containers. This software provides a graphical interface that allows you to:

- Create firewall tests;  
- Define and edit firewall rules on the scenario's hosts;  
- Add and remove ports that represent network services to be tested;  

Additionally, the software allows you to save test results and rerun them later, for example, on another computer.

## Project Organization

```
firewallTester/
├── assets/
├── core/
├── docker/
├── gns3_projects/
├── ui/
├── main.py
├── requirements.txt

```

## License

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License or (at your option) any later version.

This program is distributed in the hope that it will be useful, but **WITHOUT ANY WARRANTY**; without even the implied warranty of **MERCHANTABILITY** or **FITNESS FOR A PARTICULAR PURPOSE**. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.


## Configuration Tutorial

### Environment Prerequisites

Before opening the software, set up your virtual environment.

- Download the VirtualBox virtual machine, available at:  
  https://www.virtualbox.org/wiki/Downloads
- Install the GNS3 VM using the file available on the official GNS3 website.
- After completing the installation, configure the network settings.

### Network Settings
- Create a project in GNS3.
- Drag Docker containers into the workspace (e.g., hosts and firewalls).
- Connect them using virtual network cables.

> **Important:** Configure static IP addresses and routes either through the GNS3 network configuration (Edit Config) or via the terminal.

### Initializing FirewallTester

- With the GNS3 simulation running (Play button pressed), open the VM terminal by pressing ``Alt + Enter``.
- In the terminal, run the following command to install the required libraries:
  ```bash
  pip3 install -r requirements.txt
- After the installation, run ``python3 main.py`` to start the application.
- Once launched, the software will scan the container components.
- Check the bottom status bar or the **Hosts** tab. You should see your containers listed (e.g., `host-1`, `firewall-1`).
- If the list is empty, click **Refresh Hosts**.


### Managing Services (Hosts Tab)

**Check the server status:** ensure it is **On**, as tests will fail if the destination server is turned off.

**Editing ports:** select a host to view open ports, add new ones to simulate services, and note that the server restarts automatically to apply changes.


### Applying Security Rules (Firewall Rules Tab)

This is where you define how the firewall should behave.
 1. At the top, choose the container that will act as the firewall (e.g., `Firewall-1`).
 2. Write your firewall script (iptables syntax or shell script). Example:  ``iptables -A FORWARD -p tcp --dport 80 -j DROP``.

**Options:**
- Reset before applying: Check this option if you want to clear old rules before applying new ones.
- Apply Rules (Deploy): Sends the script to the container and executes it.
- Check the output box to confirm there are no iptables syntax errors.

### Creating and Running Tests (Firewall Tests Tab)

####  Adding a Test

Configure the fields in the **New Test** box:

- **Source:** Who sends the packet (e.g., `Host-1`).
- **Destination:** Who receives it (e.g., `Host-2`). The system automatically retrieves the IP address.
- **Protocol:** TCP, UDP, or ICMP.

  > **Note:** For ICMP (Ping), the port is ignored or treated as a count.
- **Dst Port:** The target port (e.g., `80`).

#### Expected Result

- **Allowed:** You expect the packet to reach its destination (Success).
- **Blocked:** You expect the firewall to block the packet (Timeout / Refused).

Click **Add** to place the test in the queue.

**Running Tests**

- **Test Row:** Select a test in the table and click this button to run only that test.
- **Test All:** Opens a progress window and executes the list sequentially.
- **Cancel:** If you need to stop execution, click **Cancel** in the progress window. The interruption is immediate.

**Results**

- **Green (Allowed):** Allowed was expected and the connection succeeded. The test passed.
- **Blue (Blocked):** Blocked was expected and the connection failed. The firewall worked. The test passed.
- **Red (Failed):** The actual result was different from the expected one (e.g., you expected it to be blocked, but it was allowed).
- **Yellow (Error):** Technical error (e.g., host powered off, missing route, Python script error).

## Contact

This software was developed by **Luiz Arthur Feitosa dos Santos**, professor at **UTFPR (Federal Technological University of Paraná) - Campo Mourão, Brazil**.  
Email: <luiz.arthur.feitosa.santos@gmail.com> | <luizsantos@utfpr.edu.br>
