# Scripts for Okta Verify
Details: [Okta Terrify vs macOS](https://kawakatz.io/notes/okta-terrify-vs-macos/)

## Usage
### Certificate Pinning Bypass
I will add an ARM-specific script once I obtain an ARM-based Mac (Apple Silicon).  
To implement the ARM version, I need to update the register names and review the patching method for custom certificate verification.  
```
1. Disable System Integrity Protection (SIP)
2. sudo lldb -n 'Okta Verify' -s pin-bypass-<intel/arm>.lldb
3. Execute "continue" in lldb
```

#### How It Works (for Intel Mac)
- **SecTrustEvaluate**  
  - Writes `0x1` to the memory location pointed to by the second argument.  
  - Sets the return value register (`rax`) to `0`, indicating success.
- **SecTrustEvaluateWithError**  
  - Sets the register holding the second argument (`rsi`) to `0`, thereby disabling error information.  
  - Writes `0` to the memory location that stores the error flag.  
  - Sets the return value register (`rax`) to `1`, indicating success.
- **SSL_get_psk_identity**  
  - Replaces the memory content at the return value with the string `"notarealPSKidentity\0"`
- **boringssl_context_set_verify_mode**  
  - Sets the return value register (`rax`) to `0`.
- **boringssl_context_certificate_verify_callback**  
  - Sets the return value register (`rax`) to `0`.
- **Custom Certificate Verification of Okta Verify**  
  - Sets the `bl` register to `1`, thereby bypassing verification.

### 8769/tcp Port Forwarding
This script expects a SOCKS5 proxy and proxies POST requests to `http://127.0.0.1/challenge` that are issued by Okta.
```sh
python3 poc.py --proxy-host <proxy host> --proxy-port <proxy port> --origin 'https://<company>.okta.com'
