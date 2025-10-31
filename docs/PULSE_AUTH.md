# PulseAuth - Token Mode Authentication

**Phase 2 Security Layer for PulseMesh**

Author: Brady Simmons  
Date: October 31, 2025  
Status: Specification (Not Yet Implemented)  
Copyright: © 2025 Sovereignty Foundation. All rights reserved.

---

## Overview

**PulseAuth** is the authentication and authorization system for PulseMesh, enabling secure, governed communication between distributed nodes in the Sovereignty Stack.

Currently, PulseMesh operates in **Stub Mode** (no authentication). This document specifies **Token Mode** for production deployment.

---

## Authentication Flow

### 1. Node Registration

```
Node → SAGE: Request JWT
SAGE → Node: Issue signed JWT
Node → PulseMesh: Connect with JWT
PulseMesh → SAGE: Verify JWT
SAGE → PulseMesh: Validation result
PulseMesh: Accept/Reject connection
```

### 2. JWT Structure

```json
{
  "header": {
    "alg": "RS256",
    "typ": "JWT"
  },
  "payload": {
    "node_id": "mirror",
    "role": "ui",
    "allowed_topics": [
      "mirror.intent",
      "mirror.update",
      "mirror.query"
    ],
    "iat": 1698787200,
    "exp": 1698873600,
    "iss": "sage.sovereignty.local"
  },
  "signature": "..."
}
```

### 3. Topic-Level Permissions

Each node's JWT specifies:
- **node_id**: Unique identifier
- **role**: ui | reasoner | governor | scribe | hermes
- **allowed_topics**: Array of topics node can emit to
- **expiration**: Token validity period

---

## Implementation

### SAGE JWT Issuer

**File:** `sov/core/sage_auth.py`

```python
from jose import jwt
from datetime import datetime, timedelta

class SAGEAuthority:
    def __init__(self, private_key_path: str):
        self.private_key = self._load_private_key(private_key_path)
    
    def issue_token(self, node_id: str, role: str, topics: list[str]) -> str:
        """Issue JWT for node"""
        payload = {
            "node_id": node_id,
            "role": role,
            "allowed_topics": topics,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=24),
            "iss": "sage.sovereignty.local"
        }
        return jwt.encode(payload, self.private_key, algorithm="RS256")
    
    def verify_token(self, token: str) -> dict:
        """Verify JWT signature and expiration"""
        return jwt.decode(token, self.public_key, algorithms=["RS256"])
```

### PulseMesh Token Verification

**File:** `sov/core/pulse_mesh.py` (updated)

```python
from fastapi import WebSocket, HTTPException, Depends
from jose import jwt, JWTError

async def verify_token(token: str) -> dict:
    """Verify JWT with SAGE"""
    try:
        # Verify signature and expiration
        payload = jwt.decode(token, SAGE_PUBLIC_KEY, algorithms=["RS256"])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.websocket("/ws/mesh/{topic}")
async def mesh_endpoint(
    websocket: WebSocket,
    topic: str,
    token: str = Query(...)
):
    # Verify token
    payload = await verify_token(token)
    
    # Check topic permission
    if topic not in payload["allowed_topics"]:
        await websocket.close(code=1008, reason="Unauthorized topic")
        # Log to SAGE audit
        await emit_audit_event({
            "event": "unauthorized_topic_access",
            "node_id": payload["node_id"],
            "topic": topic,
            "timestamp": datetime.utcnow()
        })
        return
    
    # Accept connection
    await websocket.accept()
    # ... rest of handler
```

### Mirror Token Request

**File:** `sov/mirror/client/src/core/pulse/PulseAuth.ts`

```typescript
export class PulseAuth {
  private token?: string;
  
  async requestToken(): Promise<string> {
    // Request JWT from SAGE
    const response = await fetch('http://localhost:8000/api/sage/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        node_id: 'mirror',
        role: 'ui'
      })
    });
    
    const { token } = await response.json();
    this.token = token;
    return token;
  }
  
  getToken(): string | undefined {
    return this.token;
  }
}
```

### PulseTransport with Auth

**File:** `sov/mirror/client/src/core/pulse/PulseTransport.ts` (updated)

```typescript
export class PulseTransport {
  private auth: PulseAuth;
  
  constructor(config: TransportConfig) {
    this.config = config;
    this.auth = new PulseAuth();
  }
  
  async connect(onMessage: (msg: PulseMessage) => void): Promise<void> {
    // Get token from SAGE
    const token = await this.auth.requestToken();
    
    // Connect with token
    const url = `${this.config.meshUrl}/ws/mesh/${this.config.topic}?token=${token}`;
    this.ws = new WebSocket(url);
    // ... rest of connection logic
  }
}
```

---

## Security Features

### 1. **Cryptographic Signatures**
- RSA-256 signing algorithm
- SAGE private key signs all tokens
- PulseMesh verifies with SAGE public key

### 2. **Token Expiration**
- Default: 24 hours
- Automatic refresh before expiration
- Revocation support via SAGE

### 3. **Topic-Level Authorization**
- Each token specifies allowed topics
- PulseMesh enforces on every emit
- Unauthorized attempts logged to SAGE

### 4. **Audit Trail**
- All auth events logged to Shadow Ledger
- Failed attempts trigger SAGE alerts
- Forensic analysis support

### 5. **Role-Based Access**
- Roles: ui, reasoner, governor, scribe, hermes
- Role determines default topic permissions
- Custom permissions per node

---

## Governance Integration

### SAGE Validation Rules

```yaml
# sov/core/sage/rules/pulse_auth.yaml

rule_001:
  name: "Token Expiration Check"
  description: "Reject expired tokens"
  condition: "token.exp < now()"
  action: deny
  audit: true

rule_002:
  name: "Topic Permission Check"
  description: "Verify node can emit to topic"
  condition: "topic not in token.allowed_topics"
  action: deny
  audit: true

rule_003:
  name: "Rate Limiting"
  description: "Prevent spam attacks"
  condition: "node.pulses_per_minute > 1000"
  action: flag
  audit: true
```

### Audit Events

```typescript
interface AuditEvent {
  event_type: 'token_issued' | 'token_verified' | 'unauthorized_access' | 'token_expired';
  node_id: string;
  topic?: string;
  timestamp: string;
  metadata: Record<string, any>;
}
```

---

## Deployment

### Development (Stub Mode)

```bash
# No authentication required
export PULSE_AUTH_MODE=stub
python3.11 pulse_mesh.py
```

### Production (Token Mode)

```bash
# Generate SAGE key pair
openssl genrsa -out sage_private.pem 2048
openssl rsa -in sage_private.pem -pubout -out sage_public.pem

# Configure PulseMesh
export PULSE_AUTH_MODE=token
export SAGE_PUBLIC_KEY_PATH=/path/to/sage_public.pem
python3.11 pulse_mesh.py
```

---

## Migration Path

### Phase 1 → Phase 2 Transition

1. **Add token support** to PulseMesh (backward compatible)
2. **Deploy SAGE auth service** alongside existing mesh
3. **Update Mirror** to request tokens
4. **Test dual-mode** (stub + token) in staging
5. **Switch production** to token-only mode
6. **Remove stub mode** after migration complete

---

## Future Enhancements

### 1. **Mutual TLS (mTLS)**
- Certificate-based authentication
- Stronger than JWT alone
- Hardware security module (HSM) support

### 2. **OAuth 2.0 Integration**
- External identity providers
- Single sign-on (SSO)
- User-level permissions

### 3. **Zero-Trust Architecture**
- Continuous verification
- Least-privilege access
- Micro-segmentation

### 4. **Quantum-Resistant Crypto**
- Post-quantum algorithms
- Future-proof security
- NIST compliance

---

## References

- [PulseMesh Architecture](/docs/PULSEMESH_ARCHITECTURE_v1.0.md)
- [SAGE Governance](/core/sage.py)
- [Shadow Ledger Provenance](/core/provenance.py)
- [JWT RFC 7519](https://tools.ietf.org/html/rfc7519)

---

**© 2025 Sovereignty Foundation. All rights reserved.**
