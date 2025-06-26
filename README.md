# Firewall Tester

This software was developed to enhance network security through practical and efficient firewall testing. More than just a testing tool, it serves as a valuable educational resource, designed to simplify and improve the learning process about firewalls. With an intuitive and interactive interface, students can visualize and experiment with firewall rule creation and application, making complex concepts easier to understand and fostering deeper, more effective learning.

The software enables the creation of network scenarios using [GNS3](https://www.gns3.com/). Hosts within the scenario should utilize Docker images to create containers for firewall testing (this version of the software supports only containers). Once the network scenario is set up in GNS3 and all hosts are powered on, you can launch the firewall rule testing software on the host running the containers. This software provides a graphical interface that allows you to:

- Create firewall tests;  
- Define and edit firewall rules on the scenario's hosts;  
- Add and remove ports that represent network services to be tested;  

Additionally, the software allows you to save test results and rerun them later, for example, on another computer.

## Project Organization

```
/firewallTester/  
    ├── src/ (source files)  
    │   ├── client.py (Acts as a client in the test scenario)  
    │   ├── server.py (Acts as a server in the test scenario)  
    │   ├── gui/  
    │       ├── guiFirewallTest.py (Graphical interface for firewall rule testing)  
    │  
    ├── docker/ (Docker-related files)  
    ├── gns3/ (GNS3 project files)  
```

## License

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License or (at your option) any later version.

This program is distributed in the hope that it will be useful, but **WITHOUT ANY WARRANTY**; without even the implied warranty of **MERCHANTABILITY** or **FITNESS FOR A PARTICULAR PURPOSE**. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

## Contact

This software was developed by **Luiz Arthur Feitosa dos Santos**, professor at **UTFPR (Federal Technological University of Paraná) - Campo Mourão, Brazil**.  
Email: <luiz.arthur.feitosa.santos@gmail.com> | <luizsantos@utfpr.edu.br>