# Scripts for Okta Verify
Details: [Okta Terrify vs macOS](https://kawakatz.io/notes/okta-terrify-vs-macos/)

## Usage
#### Certificate Pinning Bypass
I will add a script for ARM after I get an ARM Mac (Apple Silicon).  
I need to rename the registers and check the patching method for custom certificate verification.  
```
1. Disable SIP
2. sudo lldb -n 'Okta Verify' -s pin-bypass-<intel/arm>.lldb
3. Execute "continue" in lldb
```

#### 8769/tcp Port Forwarding
This script expects SOCKS5 proxies.
```sh
python3 poc.py --proxy-host <proxy host> --proxy-port <proxy port> --origin 'https://<company>.okta.com'
```
