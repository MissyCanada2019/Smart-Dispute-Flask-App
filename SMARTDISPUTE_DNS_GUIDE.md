# Domain Configuration Guide for smartdisputecanada.me

## DNS Records to Add at Your Registrar
```dns
Type: A
Name/Host: @
Value/Points to: 76.76.21.21
TTL: 3600

Type: CNAME
Name/Host: www
Value/Points to: cname.railway.app
TTL: 3600
```

## Step-by-Step Setup for Popular Registrars:

### GoDaddy:
1. Log in to GoDaddy account
2. Go to "My Products" → Domains
3. Click "DNS" next to smartdisputecanada.me
4. Click "Add Record"
5. For A record:
   - Type: A
   - Host: @
   - Points to: 76.76.21.21
   - TTL: 1 hour
6. For CNAME record:
   - Type: CNAME
   - Host: www
   - Points to: cname.railway.app
   - TTL: 1 hour
7. Click "Save"

### Namecheap:
1. Log in to Namecheap account
2. Go to "Domain List" → Manage next to smartdisputecanada.me
3. Go to "Advanced DNS"
4. Add new record:
   - Type: A Record
   - Host: @
   - Value: 76.76.21.21
   - TTL: 30 min
5. Add new record:
   - Type: CNAME Record
   - Host: www
   - Value: cname.railway.app
   - TTL: 30 min
6. Click "Save All Changes"

### Google Domains:
1. Log in to Google Domains
2. Select smartdisputecanada.me
3. Go to "DNS" section
4. Under "Custom resource records":
   - Add A record: 
     - Name: @
     - IPv4 Address: 76.76.21.21
     - TTL: 3600
   - Add CNAME record:
     - Name: www
     - Domain name: cname.railway.app
     - TTL: 3600
5. Click "Save"

## Verification:
After setup, check status with:
```bash
dig smartdisputecanada.me +noall +answer
```

## Important Notes:
1. Changes may take 24-48 hours to propagate globally
2. Railway will automatically issue SSL certificates
3. Keep your .env file updated with API keys