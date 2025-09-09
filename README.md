# Client Utility Tool

A **cross-platform client utility** for Linux, macOS, and Windows.

## Features
- Checks for:
  - Disk Encryption  
  - OS Updates  
  - Antivirus  
  - Inactivity Timeout  
- Runs in the background every **15 minutes** (default)  
- Sends checks to the server whenever there is a change  

## Getting Started

### Prerequisites
- Python 3  
- Git  

> Install them if you don’t have them already.

### Installation
1. **Clone the repository**  
```bash
git clone https://github.com/yashaspancham/client-utils-solsphere.git
```
2. **Enter the project folder**
```bash
cd client-utils-solsphere
```
3.***Add env***
```bash
echo 'CONFIG_ENV = {
    "SEND_REPORT_API":"hosted-server-url/api/reports",
    "API_KEY":"api-key"
}' > env.py
```
4.***Run Code***
```bash
python3 agent.py
```
